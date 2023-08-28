from dataclasses import dataclass
from typing import Any, List

from entities.payload import Payload


@dataclass
class FlaggedEvents:
    timed_out_events: List[Payload] = None
    failed_events: List[Payload] = None
    inappropriate_events: List[Payload] = None
    invalidated_events: List[Payload] = None
    flagged_doc_events: Any = None

    def consolidated_timed_out_events(self):
        events = []
        if self.timed_out_events is not None:
            for time_out_event in self.timed_out_events:
                event = {
                    "Document ID": time_out_event.chunk.source,
                    "Chunk ID": time_out_event.chunk.id,
                    "Reason": "Timed Out",
                    "Tokens": time_out_event.chunk.token_size,
                }
                events.append(event)
        return events

    def consolidated_failed_events(self):
        events = []
        if self.failed_events is not None:
            for failed_event in self.failed_events:
                event = {
                    "Document ID": failed_event.chunk.source,
                    "Chunk ID": failed_event.chunk.id,
                    "Reason": "Failed Api Calls",
                    "Tokens": failed_event.chunk.token_size,
                }
                events.append(event)
        return events

    def consolidated_inappropriate_events(self):
        events = []
        if self.inappropriate_events is not None:
            for inappropriate_event in self.inappropriate_events:
                event = {
                    "Document ID": inappropriate_event.chunk.source,
                    "Chunk ID": inappropriate_event.chunk.id,
                    "Reason": "Inappropriate Content",
                    "Tokens": inappropriate_event.chunk.token_size,
                }
                events.append(event)
        return events

    def consolidated_invalidated_events(self):
        events = []
        if self.invalidated_events is not None:
            for invalid_event in self.invalidated_events:
                event = {
                    "Document ID": invalid_event.chunk.source,
                    "Chunk ID": invalid_event.chunk.id,
                    "Reason": "Validation Failed",
                    "Tokens": invalid_event.chunk.token_size,
                }
                events.append(event)
        return events
