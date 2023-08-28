import base64
import io
import time

import pandas as pd
import streamlit as st
import numpy as np
import  streamlit_toggle as tog

from config import MAX_TIME_PER_CHUNK, LLM_MODEL
from entities.personal_info import is_junk_value
from entities.pricing import Pricing
from util.string_utils import parse_date


class AppUI:
    def __init__(self):
        self.documents = []
        self.toggle_status = False
        self._docs_processed_log = st.empty()
        self._chunk_processing_log = st.empty()
        self._start_job_time = time.perf_counter()
        self.logs = ""

    @staticmethod
    def get_uploaded_files():
        return st.file_uploader('Upload .txt files', type='txt', accept_multiple_files=True)
    
    @staticmethod
    def get_toggle_componet():
        return tog.st_toggle_switch(label="Pre_Classification", 
                key="Key", 
                default_value=False, 
                label_after = False, 
                inactive_color = '#D3D3D3', 
                active_color="#11567f", 
                track_color="#29B5E8"
        )
        return 

    def display_results(self, documents, combined_personal_info_list, original_personal_info_list, flagged_events):
        # Create a list of dictionaries for each document
        rows = []
        original_rows = []
        unique_rows = set()
        original_unique_rows = set()
        all_keys = set()

        # Find all unique keys in combined_personal_info
        for personal_info_list in combined_personal_info_list:
            if personal_info_list:
                # Iterate over all person dictionaries in each combined_personal_info
                for person in personal_info_list:
                    keys = person.info.dict().keys()
                    all_keys.update(keys)

        # Create mapping dictionary and columns
        columns = ['Document ID',
                   'Source',
                   'Chunk ID',
                   'Full Name',
                   'Date of Birth',
                   'Social Security Number',
                   'Full Address',
                   'Driver\'s License Number',
                   'Passport Number',
                   'Medical Record Number',
                   'Account Number',
                   'Account PIN',
                   'Security Code',
                   'Routing Number',
                   'Payment Card Number',
                   'Payment Card PIN',
                   'Expiration Date',
                   'Username with Password',
                   'Email Address with Password',
                   'Biometric Data',
                   'Medical Information',
                   'Health Insurance Information']
        error_report_columns = ['Document ID', 'Chunk ID', 'Reason', 'Tokens']

        # print(f"Columns Created: {columns}")

        # Create a dictionary for each document
        self.generate_rows(combined_personal_info_list, documents, rows, unique_rows)
        self.generate_rows(original_personal_info_list, documents, original_rows, original_unique_rows,
                           is_original=True)
        # Create the DataFrame
        df = pd.DataFrame(rows, columns=columns)
        df_flagged_events = pd.DataFrame(flagged_events, columns=error_report_columns)
        df_original_data = pd.DataFrame(original_rows, columns=columns)
        # Display the DataFrame
        st.dataframe(df)

        # Create Excel file
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Extracted Information')
            df_flagged_events.to_excel(writer, sheet_name='Flagged Events')
            df_original_data.to_excel(writer, sheet_name='Original Data')
        excel_data = output.getvalue()

        return base64.b64encode(excel_data).decode()

    @staticmethod
    def generate_rows(combined_personal_info_list, documents, rows, unique_rows, is_original=False):
        for doc, personal_info_list in zip(documents, combined_personal_info_list):
            for person in personal_info_list:
                if not is_original and (
                        not person.info.persons_full_name or is_junk_value(person.info, person.info.persons_full_name)):
                    continue
                person_info_dict = person.info.dict()
                has_other_info = any(
                    value for key, value in person_info_dict.items() if
                    key != 'persons_full_name' and key != 'chunk_id')

                # Only add person_info to rows if it has other info besides full name
                if has_other_info or is_original:
                    row = {
                        'Document ID': doc.id,
                        'Source': doc.source,
                        'Chunk ID': person.source,
                        'Full Name': person.info.persons_full_name,
                        'Date of Birth': parse_date(
                            person.info.date_of_birth) if not is_original else person.info.date_of_birth,
                        'Social Security Number': person.info.social_security_number,
                        'Full Address': person.info.full_address,
                        'Driver\'s License Number': person.info.drivers_license_number,
                        'Passport Number': person.info.passport_number,
                        'Medical Record Number': person.info.medical_record_number,
                        'Account Number': 'Yes' if person.info.has_account_number else '',
                        'Account PIN': 'Yes' if person.info.has_bank_account_pin else '',
                        'Security Code': 'Yes' if person.info.has_credit_card_security_code else '',
                        'Routing Number': 'Yes' if person.info.has_routing_number else '',
                        'Payment Card Number': 'Yes' if person.info.has_payment_card_number else '',
                        'Payment Card PIN': 'Yes' if person.info.has_payment_card_pin else '',
                        'Expiration Date': 'Yes' if person.info.has_expiration_date else '',
                        'Username with Password': 'Yes' if person.info.has_account_username_with_password else '',
                        'Email Address with Password': 'Yes' if person.info.has_email_address_with_password else '',
                        'Biometric Data': 'Yes' if person.info.has_biometric_data else '',
                        'Medical Information': 'Yes' if person.info.has_medical_information else '',
                        'Health Insurance Information': 'Yes' if person.info.has_health_insurance_information else '',
                    }
                    # Convert row dictionary to a hashable type
                    row_items = tuple(sorted(row.items()))
                    if row_items not in unique_rows:
                        unique_rows.add(row_items)
                        rows.append(row)

    @staticmethod
    def display_logs(logs):
        st.text_area("Logs", logs, height=200)

    def update_docs_processed_ui_log(self, docs_processed_text):
        self._docs_processed_log.text(docs_processed_text)

    def update_chunk_processing_ui_log(self, chunk_processing_text):
        self._chunk_processing_log.text(chunk_processing_text)

    def add_to_logs(self, log):
        self.logs += log + "\n"

    @staticmethod
    def display_timed_out_chunks_data(timed_out_chunks_count):
        st.markdown(
            f"**Total Timed Out Chunks:** {timed_out_chunks_count}"
            f" | Max Allowed Time per Chunk: {MAX_TIME_PER_CHUNK:.2f} seconds")

    @staticmethod
    def display_all_timed_out_chunks(timed_out_chunks):
        if len(timed_out_chunks) > 0:
            expander = st.expander("Display all Timed Out Chunks")
            for i, result in enumerate(timed_out_chunks):
                chunk = result.chunk
                with expander:
                    st.text(f'{chunk.id}-{chunk.source}')
                    st.text({chunk.text[:150]})

    @staticmethod
    def display_all_inappropriate_chunks(inappropriate_chunks):
        if len(inappropriate_chunks) > 0:
            inappropriate_chunks_tab = st.expander("Display all Flagged Inappropriate Chunks")
            with inappropriate_chunks_tab:
                for i, result in enumerate(inappropriate_chunks):
                    chunk = result.chunk
                    st.text(f'{chunk.id}-{chunk.source}:\n {chunk.text[:150]}')

    @staticmethod
    def display_all_failed_chunks(failed_chunks):
        if len(failed_chunks) > 0:
            failed_chunks_tab = st.expander("Display all Failed Chunks")
            with failed_chunks_tab:
                for i, result in enumerate(failed_chunks):
                    chunk = result.chunk
                    st.text(f'{chunk.id}-{chunk.source}:\n {chunk.text[:150]}')

    # displays a list of all documents containing flagged chucks
    @staticmethod
    def display_flagged_documents_events(flagged_documents):
        if len(flagged_documents) > 0:
            expander = st.expander(f'{len(flagged_documents)} Flagged Documents for additional review')
            with expander:
                for doc in flagged_documents:
                    st.text(f'{doc}')

    def display_totals_and_elapsed_time(self, job_analytics):
        total_processing_time = time.perf_counter() - self._start_job_time
        average_processing_time_per_chunk = total_processing_time / job_analytics.total_chunks

        self.add_to_logs(f"Total tokens estimated for all documents: {job_analytics.tokens_estimated}")
        self.add_to_logs(f"Total chunks created for all documents: {job_analytics.total_chunks}")
        self.add_to_logs(f"Average processing time per chunk: {average_processing_time_per_chunk:.2f} seconds")
        cost_estimated = (job_analytics.tokens_estimated / 1000) * Pricing.COST_PER_1000_TOKENS[LLM_MODEL]
        self.display_logs(self.logs)

        col1, col2, col3, col4 = st.columns(4)
        col1.markdown(f"**Total documents:** {job_analytics.total_documents}")
        col2.markdown(f"**Total Chunks Created** {job_analytics.total_chunks}")
        col3.markdown(f"**Total tokens Est:** {job_analytics.tokens_estimated}")
        col4.markdown(f"**Cost Estimate:** ${cost_estimated:.4f}")
        col1_2, col2_2, col3_2, col4_2 = st.columns(4)
        col1_2.markdown(f"**Avg Time per chunk:** {average_processing_time_per_chunk:.2f} seconds")
        col2_2.markdown(f"**Total Time for Job:** {total_processing_time:.2f} seconds")
        col3_2.markdown(f"**Total tokens used:** {job_analytics.total_tokens_used}")
        col4_2.markdown(f"**Total Cost:** ${job_analytics.total_cost:.4f}")
        col1_3, col2_3, col3_3, col4_3, col5_3 = st.columns(5)
        col1_3.markdown(f"**Most Time by Chunk:** {job_analytics.longest_chunk_processing_time:.2f} seconds")
        col2_3.markdown(f"**Least Time by Chunk:** {job_analytics.shortest_chunk_processing_time:.2f} seconds")
        col3_3.markdown(f"**Most Chunks Created Per Doc:** {job_analytics.most_chunks_created}")
        col4_3.markdown(f"**Documents Not Chunked** {job_analytics.documents_not_chunked}")
        col5_3.markdown(f"**Number of Chunks without Entities** {job_analytics.number_no_entities_found_chunks}")
        col1_4, col2_4, col3_4, col4_4 = st.columns(4)
        col1_4.markdown(f"**Total Timed Out Chunks:** {job_analytics.timed_out_chunks_count}")
        col2_4.markdown(f"**Total Failed Chunks:** {job_analytics.failed_chunks_count}")
        col3_4.markdown(f"**Chunks Flagged Inappropriate:** {job_analytics.chunks_flagged_inappropriate}")
        col4_4.markdown(f"**Total Validation Errors:** {job_analytics.validation_errors}")

    def complete_job(self, combined_personal_info_list, original_personal_info_list, flagged_events):
        if len(st.session_state.documents) == 0:
            st.session_state.documents = self.documents
        # Display the DataFrame and get the Excel data
        excel_data = self.display_results(st.session_state.documents, combined_personal_info_list,
                                          original_personal_info_list, flagged_events)
        # Create a download button for the Excel file
        st.download_button(
            label="Download results",
            data=base64.b64decode(excel_data),
            file_name='results.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
