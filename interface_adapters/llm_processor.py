from abc import ABC, abstractmethod


class LLMProcessor(ABC):
    @abstractmethod
    async def agenerate_extraction(self, input_text, document_name, chunk_id):
        pass

    @abstractmethod
    async def asequential_generate(self, input_text):
        pass

    @property
    @abstractmethod
    def parser(self):
        pass
