# File: use_cases/concurrent_task_manager.py
import asyncio
import datetime
import json
import re
import time
from threading import Thread

import aiohttp
from aioprocessing import AioJoinableQueue, AioQueue
from langchain.callbacks import get_openai_callback
from tenacity import AsyncRetrying, stop_after_attempt, wait_random_exponential, RetryError

from config import LLM_MODEL
from entities.payload import Payload
from entities.personal_info import sanitize_object
from entities.personal_info_list import PersonalInfoList
from entities.pricing import Pricing


class ConcurrentApiTaskManager:
    def __init__(self, concurrency, llm_processor):
        self._loop = asyncio.new_event_loop()
        self._in_queue = AioJoinableQueue(maxsize=concurrency)
        self._out_queue = AioQueue(maxsize=concurrency)
        self._event_loop_thread = Thread(target=self._run_event_loop)
        self._event_loop_thread.start()
        self._workers = []
        self._session = aiohttp.ClientSession()
        self.concurrency = concurrency
        self.llm_processor = llm_processor

        for i in range(concurrency):
            asyncio.run_coroutine_threadsafe(self._worker(i), self._loop)

    def _run_event_loop(self):
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    async def _process_payload(self, payload, retry_count=0, retry_input=None):
        print(f"Processing chunk {payload.chunk.id}, attempt {retry_count}")
        response_text = None
        try:
            with get_openai_callback() as cb:
                start_time = datetime.datetime.now()
                try:
                    print(f'''Processing chunk: {payload.chunk.id}\n
                        Token count: {payload.chunk.token_size}\n
                        Char count: {payload.chunk.char_size}\n
                        START_TIME: {start_time}\n''')

                    total_processing_time = 0
                    s = time.perf_counter()
                    if retry_input is not None:
                        extraction_prompt = self.llm_processor.prompt_creator.create_extraction_prompt()
                        prompt_value = extraction_prompt.format_prompt(input=payload.chunk.text)
                        retry_output = self.llm_processor.retry_parser.parse_with_prompt(retry_input, prompt_value)

                        personal_info_list_output = PersonalInfoList(data=retry_output.data)
                        payload.output = personal_info_list_output
                    else:
                        response = await asyncio.wait_for(
                            self.llm_processor.agenerate_extraction([{"input": payload.chunk.text}],
                                                                    payload.chunk.source, payload.chunk.id),
                            timeout=payload.time_limit)
                        response_text = response.text
                        sanitized_output = self.llm_processor.parser.parse(response_text)
                        payload.output = sanitized_output
                        if response.total_tokens > 0:
                            cb.total_tokens = response.total_tokens

                except asyncio.TimeoutError:
                    if retry_count > 5:
                        print(f"FINAL: TimeoutError processing chunk {payload.chunk.id}, marking as timed_out")
                        payload.output = PersonalInfoList(data=[])
                        payload.timed_out = True
                    else:
                        new_retry_count = retry_count + 1
                        print(
                            f"TimeoutError processing chunk {payload.chunk.id},"
                            f" retrying; new_retry_count: {new_retry_count}")
                        await asyncio.sleep(2 + new_retry_count)
                        await self._process_payload(payload, new_retry_count)

                elapsed = time.perf_counter() - s
                total_processing_time += elapsed
                # print(f"PROCESS_PAYLOAD: Chunk {payload.chunk.id} took {elapsed:0.2f} seconds to process")
                # print(f"PROCESS_PAYLOAD: Chunk {payload.chunk.id} output: {payload.output}\n")
                sanitized_data = []
                original_data = []
                for item in payload.output.data:
                    sanitized_item, replaced_info = sanitize_object(item)
                    print(f"Replaced Values: {replaced_info}")
                    original_data.append(replaced_info)
                    sanitized_data.append(sanitized_item)

                    if item.is_potential_hallucination():
                        payload.potential_hallucinations_count += 1

                    print(f"SANITIZED - Chunk {payload.chunk.id} output: {sanitized_item}\n")

                payload.output.data = sanitized_data
                payload.original_output = PersonalInfoList(data=original_data)

                payload.processing_time = total_processing_time
                payload.total_tokens_used = cb.total_tokens
                payload.total_cost = (cb.total_tokens / 1000) * Pricing.COST_PER_1000_TOKENS[LLM_MODEL]
                return payload
        except Exception as e:
            print(f"Error processing chunk {payload.chunk.id}, error: {e}")
            if "error: This model's maximum context length is" in str(e):
                print(f"FINAL: Chunk {payload.chunk.id} exceeded max response length, marking as failed")
                payload.validation_error = True
                payload.output = PersonalInfoList(data=[])
                payload.total_tokens_used = cb.total_tokens
                payload.total_cost = (cb.total_tokens / 1000) * .0015
                return payload
            if "Failed to parse" in str(e) and response_text or retry_input is not None:
                if retry_count >= 2:
                    if 'value_error.missing' in str(e):
                        # ignore missing fields and pass the existing data through anyway
                        try:
                            print(f"Failed to parse PersonalInfoList, ignoring missing fields")
                            sanitized_data = []
                            data_dict = json.loads(retry_input).get('data', [])
                            for item in data_dict:
                                if 'has_biometric_data' not in item:
                                    item['has_biometric_data'] = False
                                if 'has_medical_information' not in item:
                                    item['has_medical_information'] = False
                                if 'contains_health_insurance_information' not in item:
                                    item['contains_health_insurance_information'] = False
                                sanitized_data.append(item)
                            payload.output = PersonalInfoList(data=sanitized_data)
                        except Exception as e:
                            print(f"FINAL: Failed to parse PersonalInfoList, marking as validation error: {e}")
                            payload.validation_error = True
                            payload.output = PersonalInfoList(data=[])
                            payload.total_tokens_used = cb.total_tokens
                            payload.total_cost = (cb.total_tokens / 1000) * .0015
                        return payload
                    else:
                        print(f"FINAL: Failed to parse PersonalInfoList, marking as validation error")
                        payload.validation_error = True
                else:
                    if response_text is None:
                        response_text = retry_input
                    new_retry_count = retry_count + 1
                    print(f"Failed to parse PersonalInfoList, retrying; new_retry_count: {new_retry_count}")
                    print(f"To retry with: {response_text}")
                    cleaned_response_output = re.sub(r'"\w+": null,?', '', response_text)
                    if cleaned_response_output == '{"data": {}}':
                        cleaned_response_output = '{"data": []}'
                    await asyncio.sleep(2 + new_retry_count)
                    return await self._process_payload(payload, new_retry_count, cleaned_response_output.strip())

            payload.output = PersonalInfoList(data=[])  # return an output object with an empty data attribute
            payload.total_tokens_used = cb.total_tokens
            payload.total_cost = (cb.total_tokens / 1000) * .0015
            if "Azure has not provided the response due to a content filter being triggered" in str(e):
                payload.flagged_inappropriate = True
            elif "error: 'NoneType' object" in str(e):
                print(f"Error processing chunk {payload.chunk.id}, marking as no_entities_found")
                payload.no_entities_found = True
            else:
                print(f"Error processing chunk {payload.chunk.id}, marking as failed")
                payload.failed = True
            return payload

    async def _worker(self, i):
        chunks_processed = 0
        chunks_failed = 0
        while True:
            payload_data = await self._in_queue.coro_get()
            payload = Payload.from_dict(payload_data) if payload_data is not None else None
            # Stop if None is in the queue or if the queue is empty
            if payload is None:
                self._in_queue.task_done()
                break
            else:
                print(f"Worker {i} got payload {payload.chunk.id} source {payload.chunk.source}")
            try:
                print(f"Worker {i} processing chunk {payload.chunk.id} START_TIME: {datetime.datetime.now()}")
                async for attempt in AsyncRetrying(
                        wait=wait_random_exponential(multiplier=1, max=120),
                        stop=stop_after_attempt(5)
                ):
                    with attempt:
                        try:
                            payload.attempt = attempt.retry_state.attempt_number
                            print(f"Worker {i} processing chunk {payload.chunk.id} attempt {payload.attempt}")
                            payload = await self._process_payload(payload)
                            chunks_processed += 1
                            chunks_failed += 1 if payload.failed else chunks_failed
                            print(f"Worker {i} finished processing chunk {payload.chunk.id} attempt {payload.attempt}")
                            print(f"Remaining queue size: {self._in_queue.qsize()}")
                            print(f"{chunks_processed} chunks processed, {chunks_failed} chunks failed")
                            await self._out_queue.coro_put(payload)
                            self._in_queue.task_done()
                        except Exception as e:
                            print(f"Worker {i} failed to process chunk {payload.chunk.id} exception: {e}")
                            raise
            except RetryError as e:
                payload.failed = True
                print(
                    f"Worker {i} failed to process chunk {payload.chunk.id} after {e.last_attempt.attempt_number} attempts")
                print(f"RetryError: {e}")
                payload.failed = True
                chunks_failed += 1
                await self._out_queue.put(payload)
                self._in_queue.task_done()
            await asyncio.sleep(0)

    def close(self):
        try:
            for i in range(self.concurrency):
                self._in_queue.put(None)
            self._in_queue.join()
            self._out_queue.put(None)
            self._loop.call_soon_threadsafe(self._loop.stop)
            self._event_loop_thread.join()
            self._loop.call_soon_threadsafe(self._session.close)
        except Exception as e:
            print(f"Error closing: {e}")

    def request(self, payload):
        print("Adding payload to in_queue")
        self._in_queue.put(payload.to_dict())

    def __iter__(self):
        return self

    def __next__(self):
        result = self._out_queue.get()
        if result is None:
            raise StopIteration
        return result

    def pull_all(self):
        for _ in self:
            pass
