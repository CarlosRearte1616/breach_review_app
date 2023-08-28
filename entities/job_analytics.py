class JobAnalytics:
    def __init__(self):
        self.total_documents = 0
        self.processed_documents = 0
        self.processed_chunks = 0
        self.total_chunks = 0
        self.total_tokens_used = 0
        self.tokens_estimated = 0
        self.total_cost = 0
        self.shortest_chunk_processing_time = 0
        self.longest_chunk_processing_time = 0
        self.most_chunks_created = 0
        self.successful_retries = 0
        self.failed_retries = 0
        self.longest_retry_time = 0
        self.timed_out_chunks_count = 0
        self.failed_chunks_count = 0
        self.documents_not_chunked = 0
        self.potential_hallucinations = 0
        self.chunks_flagged_inappropriate = 0
        self.number_no_entities_found_chunks = 0
        self.validation_errors = 0

    def update_most_chunks_created(self, chunks_created_count):
        if chunks_created_count > self.most_chunks_created:
            self.most_chunks_created = chunks_created_count

    def update_longest_chunk_processing_time(self, chunk_processing_time):
        if chunk_processing_time > self.longest_chunk_processing_time:
            self.longest_chunk_processing_time = chunk_processing_time

    def update_shortest_chunk_processing_time(self, chunk_processing_time):
        if chunk_processing_time < self.shortest_chunk_processing_time:
            self.shortest_chunk_processing_time = chunk_processing_time
