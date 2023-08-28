import asyncio
import logging
import sys

import streamlit as st

from entities.flagged_events import FlaggedEvents
from entities.job_analytics import JobAnalytics
from frameworks_and_drivers.fake_datastore import FakeDatastore
from frameworks_and_drivers.llms.langchain_processor import LangchainProcessor
from interface_adapters.app_ui import AppUI
from interface_adapters.document_processing_service import DocumentProcessingService


def run_app():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    stream_handler = logging.StreamHandler()
    logger.addHandler(stream_handler)

    print("Running app")
    if sys.platform == 'win32':
        loop = asyncio.ProactorEventLoop()
    else:
        loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    if 'is_initialized' not in st.session_state:
        st.session_state.is_initialized = True
        st.session_state.processed_files = []
        st.session_state.combined_results = []
        st.session_state.original_results = []
        st.session_state.documents = []
        st.session_state.flagged_events = FlaggedEvents()
        st.session_state.job_analytics = JobAnalytics()

    ui = AppUI()
    doc_processor = DocumentProcessingService(
        llm_processor=LangchainProcessor(), database=FakeDatastore("fake_db"), ui=ui
    )

    # Main application loop
    toggle_status = ui.get_toggle_componet()
    st.session_state.toggle_status = toggle_status
    ui.toggle_status = toggle_status
    
    uploaded_files = ui.get_uploaded_files()
    if len(st.session_state.processed_files) > 0:
        update_ui(st.session_state.combined_results,
                  st.session_state.original_results,
                  st.session_state.flagged_events,
                  st.session_state.job_analytics,
                  ui)

    elif uploaded_files:
        # process all uploaded files with DocumentProcessingService

        print("Retry Not in session state, processing documents normally")
        combined_results, original_personal_info_list, job_analytics, flagged_events = doc_processor.process_documents(
            uploaded_files)

        update_ui(combined_results, original_personal_info_list, flagged_events, job_analytics, ui)
        st.session_state.processed_files = uploaded_files
        st.session_state.combined_results.extend(combined_results)
        st.session_state.original_results.extend(original_personal_info_list)
        st.session_state.flagged_events = flagged_events
        st.session_state.job_analytics = job_analytics

    else:
        st.write('No file uploaded')


def update_ui(combined_results, original_personal_info_list, flagged_events, job_analytics, ui):
    ui.update_docs_processed_ui_log(f'Processed {job_analytics.processed_documents} '
                                    f'out of {job_analytics.total_documents} documents')
    ui.display_timed_out_chunks_data(job_analytics.timed_out_chunks_count)
    ui.display_all_timed_out_chunks(flagged_events.timed_out_events)
    ui.display_all_failed_chunks(flagged_events.failed_events)
    ui.display_all_inappropriate_chunks(flagged_events.inappropriate_events)
    ui.display_flagged_documents_events(flagged_events.flagged_doc_events)
    # Display the logs in a text_area with a fixed height
    ui.display_totals_and_elapsed_time(job_analytics)
    # complete job and display final results
    all_flagged_events = []
    all_flagged_events.extend(flagged_events.consolidated_timed_out_events())
    all_flagged_events.extend(flagged_events.consolidated_failed_events())
    all_flagged_events.extend(flagged_events.consolidated_inappropriate_events())
    all_flagged_events.extend(flagged_events.consolidated_invalidated_events())
    print(f"COMBINED RESULTS: {combined_results}")
    print(f"ORIGINAL RESULTS: {original_personal_info_list}")
    ui.complete_job(combined_results, original_personal_info_list, all_flagged_events)
