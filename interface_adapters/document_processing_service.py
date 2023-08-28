import re
import time
from typing import List
import codecs

from langchain.output_parsers import PydanticOutputParser
from langchain.text_splitter import TokenTextSplitter

import config
from config import MAX_TIME_PER_CHUNK, MAX_CHUNK_SIZE, CHUNK_OVERLAP, MAX_BATCH_SIZE
from entities.chunk import Chunk
from entities.document import generate_doc
from entities.flagged_events import FlaggedEvents
from entities.job_analytics import JobAnalytics
from entities.model import Model
from entities.payload import Payload
from entities.personal_info import PersonalInfoWithChunkSource
from entities.personal_info_list import PersonalInfoList
from entities.pricing import Pricing
from interface_adapters.chunk_repository import ChunkRepository
from use_cases.concurrent_api_task_manager import ConcurrentApiTaskManager
from use_cases.document_analyzer import DocumentAnalyzer
from use_cases.document_splitter import DocumentSplitter
from use_cases.prompt_templates.chat_prompt_creator import ChatPromptCreator
from util.list_utils import deduplicate_documents


class DocumentProcessingService:
    def __init__(self, llm_processor, database, ui):
        self.ui = ui
        self._llm_processor = llm_processor
        self.chunk_repository = ChunkRepository(database)
        self.api_task_manager = ConcurrentApiTaskManager(config.MAX_CONCURRENT_WORKERS, self._llm_processor)
        self.parser = PydanticOutputParser(pydantic_object=PersonalInfoList)
        self.analyzer = DocumentAnalyzer()
        self.splitter = DocumentSplitter(TokenTextSplitter(chunk_size=MAX_CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP))

    @staticmethod
    def remove_empty_dicts(list_of_dicts):
        return [d for d in list_of_dicts if d]

    def _generate_payloads(self, uploaded_file, job_analytics):
        generated_payloads = []
        file_details = {"FileName": uploaded_file.name, "FileType": uploaded_file.type,
                        "FileSize": uploaded_file.size}
        self.ui.add_to_logs(str(file_details))
        # Generate the document entity
        document = generate_doc(uploaded_file)
        # Remove BOM if present
        document.text = document.text.lstrip(codecs.BOM_UTF8.decode('utf8'))
        # Remove carriage returns and line breaks
        document.text = document.text.replace('\r', ' ').replace('\n', ' ')
        # Remove excess whitespace
        document.text = re.sub(' +', ' ', document.text)
        # Analyze the document
        token_count = self.analyzer.estimate_token_count(document.text)
        job_analytics.tokens_estimated += token_count

        # Check if the document content is not empty
        if not document.text.strip() or token_count < 10:
            self.ui.add_to_logs(f"Skipping document {uploaded_file.name} as it is empty.")
            job_analytics.total_documents -= 1
            return

        self.ui.add_to_logs(f"""Tokens estimated for document:
                Total: {token_count}
                Cost: {Pricing.calculate_cost(Model.GPT3_5_TURBO_0613, token_count)}""")
        print(self.ui.logs)

        # Split the document into chunks
        chunks = self.split_document_into_chunks(document, job_analytics)

        document_not_chunked = len(chunks) == 1

        avg_tokens_in_chunks = sum([self.analyzer.estimate_token_count(chunk) for chunk in chunks]) / len(chunks)
        avg_length_of_chunks = sum([len(chunk) for chunk in chunks]) / len(chunks)
        self.ui.update_docs_processed_ui_log(f'''{len(chunks)} chunks created
                avg of {avg_tokens_in_chunks} tokens per chunk
                avg of {avg_length_of_chunks} characters per chunk
                ''')
        print(self.ui.logs)

        # Analyze the initial prompt
        prompt_creator = ChatPromptCreator(llm=self._llm_processor.llm)
        init_prompt = prompt_creator.create_extraction_prompt()
        instructions = self.parser.get_format_instructions()
        init_prompt_text = \
            init_prompt.messages[0].format_messages(input="", format_instructions=instructions)[0].content
        tokens_in_prompt = self.analyzer.estimate_token_count(init_prompt_text)
        self.ui.add_to_logs(f"Tokens in init_prompt: {tokens_in_prompt}")
        job_analytics.tokens_estimated += tokens_in_prompt * len(chunks)

        # Create a chunk entity for each chunk
        # Save each chunk to the datastore
        # Create a payload for each chunk and add it to the api_task_manager queue
        self.ui.documents.append(document)

        for i, chunk in enumerate(chunks):
            # Save chunk
            chunk = Chunk(f'{document.id}-{i}',
                          chunk,
                          uploaded_file.name,
                          self.analyzer.estimate_token_count(chunk),
                          len(chunk))
            self.chunk_repository.save_chunk(chunk)
            payload = Payload(
                chunk=chunk,
                time_limit=MAX_TIME_PER_CHUNK,
                index=len(generated_payloads) + 1,
                not_chunked=document_not_chunked,
            )
            generated_payloads.append(payload)
            self.ui.update_chunk_processing_ui_log(f'Created {len(generated_payloads)} chunk payloads')
            print(f"App: Running Api Task Manager request: payload = {payload.chunk.id}")

        print(self.ui.logs)
        return generated_payloads

    def split_document_into_chunks(self, document, job_analytics):
        self.ui.add_to_logs("Starting chunking")
        chunks = self.splitter.split_document(document)
        job_analytics.total_chunks += len(chunks)
        job_analytics.update_most_chunks_created(len(chunks))
        return chunks

    @staticmethod
    def _batch_generator(data, batch_size):
        for i in range(0, len(data), batch_size):
            yield data[i:i + batch_size]

    def process_documents(self, uploaded_files):
        # Initialize list to store combined_personal_info for each document
        flagged_doc_events = []
        job_analytics = JobAnalytics()
        job_analytics.total_documents = len(uploaded_files)
        self.ui.add_to_logs(f'Starting job for {job_analytics.total_documents} Document(s)')
        self.ui.update_docs_processed_ui_log(f'Uploaded {job_analytics.total_documents} documents')

        payloads_generated = []
        for uploaded_file in uploaded_files:
            payloads = self._generate_payloads(uploaded_file, job_analytics)
            if payloads is None:
                continue
            payloads_generated.extend(payloads)
            job_analytics.processed_documents += 1
            self.ui.update_docs_processed_ui_log(f'Processing {job_analytics.processed_documents}'
                                                 f' out of {job_analytics.total_documents} documents')
            print(self.ui.logs)

        # This list will store the results from all payloads
        all_results: List[Payload] = []

        combined_personal_info_list, original_personal_info_list, flagged_events = self.process_payloads(all_results,
                                                                                                         flagged_doc_events,
                                                                                                         job_analytics,
                                                                                                         payloads_generated)

        return combined_personal_info_list, original_personal_info_list, job_analytics, flagged_events

    def process_payloads(self, all_results, flagged_doc_events, job_analytics,
                         payloads_generated):
        # Process each payload in batches of config.MAX_BATCH_SIZE
        for i, batch_payloads in enumerate(self._batch_generator(payloads_generated, MAX_BATCH_SIZE)):
            if i > 1:
                time.sleep(5)
            # Process the payloads and wait for tasks to finish
            job_analytics.processed_chunks += len(batch_payloads)
            self.ui.update_chunk_processing_ui_log(f'Processing {job_analytics.processed_chunks}'
                                                   f' out of {job_analytics.total_chunks} chunks')
            for payload in batch_payloads:
                self.api_task_manager.request(payload)

            self.api_task_manager.close()
            results = list(self.api_task_manager)

            # Re-initialize the manager for next iteration
            self.api_task_manager = ConcurrentApiTaskManager(concurrency=self.api_task_manager.concurrency,
                                                             llm_processor=self.api_task_manager.llm_processor)
            self.ui.update_chunk_processing_ui_log(
                f"Finished processing {job_analytics.processed_chunks} chunks out of {len(payloads_generated)}")
            # Append the results from this chunk to the all_results list
            all_results.extend(results)
        print("Doc Processing Service: All chunks finished processing")
        timed_out_chunks = []
        inappropriate_chunks = []
        failed_chunks = []
        invalidated_chunks = []
        successful_retries = 0
        longest_retry_time = 0
        total_chunks = 0
        combined_personal_info_list = []
        original_personal_info_list = []
        chunks_dict = {doc.source: [] for doc in self.ui.documents}
        print("Doc Processing Service: Processing results")
        for result in all_results:
            total_chunks += 1
            print(f"Result: {result.chunk.id} from {result.chunk.source} in {result.processing_time:.2f} seconds")
            if result.timed_out:
                print(f"App.py: Chunk {result.chunk.id} timed out from document {result.chunk.source}")
                timed_out_chunks.append(result)
                flagged_doc_events.append({"Document": f"{result.chunk.source}", "Reason": "Timed out"})
                continue
            if result.failed:
                print(f"App.py: Chunk {result.chunk.id} failed from document {result.chunk.source}")
                job_analytics.failed_chunks_count += 1
                failed_chunks.append(result)
                flagged_doc_events.append({"Document": f"{result.chunk.source}", "Reason": "Failed"})
                continue
            if result.retry_processing_time > 0:
                successful_retries += 1
                if result.retry_processing_time > longest_retry_time:
                    longest_retry_time = result.retry_processing_time
            if result.not_chunked:
                job_analytics.documents_not_chunked += 1

            if result.flagged_inappropriate:
                job_analytics.chunks_flagged_inappropriate += 1
                inappropriate_chunks.append(result)
                flagged_doc_events.append({"Document": f"{result.chunk.source}", "Reason": "Inappropriate"})

            if result.potential_hallucinations_count > 0:
                job_analytics.potential_hallucinations += result.potential_hallucinations_count
            if result.validation_error:
                job_analytics.validation_errors += 1
                invalidated_chunks.append(result)
                flagged_doc_events.append({"Document": f"{result.chunk.source}", "Reason": "Validation Error"})
            if result.no_entities_found:
                job_analytics.number_no_entities_found_chunks += 1

            # self.ui.add_to_logs(
            #     f'Chunk {result.chunk.id}\n '
            #     f'Total tokens: {result.total_tokens_used}\n '
            #     f'Cost: {result.total_cost}')
            self.ui.add_to_logs(f'Processing time: {result.processing_time:.2f} seconds')
            job_analytics.update_longest_chunk_processing_time(result.processing_time)
            job_analytics.update_shortest_chunk_processing_time(result.processing_time)

            print(self.ui.logs)
            job_analytics.total_tokens_used += result.total_tokens_used
            job_analytics.total_cost += result.total_cost
            chunks_dict[result.chunk.source].append(result)
        job_analytics.timed_out_chunks_count = len(timed_out_chunks)
        print(f"App.py: Finished waiting for {total_chunks} chunks to finish processing")
        for source, all_results in chunks_dict.items():
            personal_info_list = []  # Clear the list at the start of each iteration
            original_info_list = []
            for result in all_results:
                if result.timed_out or result.failed:
                    continue
                info_with_source_list = []
                original_info_with_source_list = []
                for item in result.output.data:
                    info_with_source_list.append(
                        PersonalInfoWithChunkSource(item, f'{result.chunk.id}'))
                for item in result.original_output.data:
                    original_info_with_source_list.append(
                        PersonalInfoWithChunkSource(item, f'{result.chunk.id}'))
                personal_info_list.extend(info_with_source_list)
                original_info_list.extend(original_info_with_source_list)
            combined_personal_info_list.append(personal_info_list)
            original_personal_info_list.append(original_info_list)
        # Remove duplicates from the combined list
        # final_combined_list = deduplicate_nested_list(combined_personal_info_list)
        flagged_doc_events = deduplicate_documents(flagged_doc_events)
        flagged_events = FlaggedEvents(timed_out_events=timed_out_chunks,
                                       failed_events=failed_chunks,
                                       inappropriate_events=inappropriate_chunks,
                                       flagged_doc_events=flagged_doc_events,
                                       invalidated_events=invalidated_chunks, )

        return combined_personal_info_list, original_personal_info_list, flagged_events
