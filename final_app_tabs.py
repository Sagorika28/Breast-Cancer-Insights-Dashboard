from final_app_demographics import demographics
from final_app_tumor import tumor_characteristics
from final_app_survival_analysis import survival_analysis
from final_app_genome import genome_dashboard

import streamlit as st


def all_tabs():
    if st.session_state.page in ['Dashboard', 'Demographics']:
        demographics()
    if st.session_state.page == 'Tumor':
        tumor_characteristics()
    if st.session_state.page == 'Survival':
        survival_analysis()
    if st.session_state.page == 'Genome':
        genome_dashboard()