from dataclasses import dataclass
from typing import Any

from entities.chunk import Chunk


@dataclass
class Payload:
    chunk: Chunk
    time_limit: float
    output: Any = None
    original_output = None
    error: Any = None
    total_tokens_used: int = 0
    total_cost: int = 0
    attempt: int = 0
    processing_time: int = 0
    retry_processing_time: int = 0
    failed: bool = False
    index: int = 0
    timed_out: bool = False
    not_chunked: bool = False
    potential_hallucinations_count: int = 0
    flagged_inappropriate: bool = False
    validation_error: bool = False
    no_entities_found: bool = False

    def to_dict(self):
        return {
            'chunk': self.chunk.to_dict() if self.chunk is not None else None,  # Assuming Chunk has a to_dict method
            'time_limit': self.time_limit,
            'output': self.output,
            'error': str(self.error) if self.error is not None else None,  # Convert error to string
            'total_tokens_used': self.total_tokens_used,
            'total_cost': self.total_cost,
            'attempt': self.attempt,
            'processing_time': self.processing_time,
            'retry_processing_time': self.retry_processing_time,
            'failed': self.failed,
            'index': self.index,
            'timed_out': self.timed_out,
            'not_chunked': self.not_chunked,
            'potential_hallucinations_count': self.potential_hallucinations_count,
            'flagged_inappropriate': self.flagged_inappropriate,
            'validation_error': self.validation_error,
        }

    @classmethod
    def from_dict(cls, data):
        data['chunk'] = Chunk.from_dict(data['chunk']) if data['chunk'] is not None else None
        data['error'] = Exception(data['error']) if data['error'] is not None else None
        return cls(**data)
