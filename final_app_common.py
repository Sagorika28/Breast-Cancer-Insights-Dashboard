import streamlit as st
import pandas as pd

min_year, max_year = 1975, 2021

age_group_options = [
    '5-14 yrs',
    '15-24 yrs',
    '25-34 yrs',
    '35-44 yrs',
    '45-54 yrs',
    '55-64 yrs',
    '65-74 yrs',
    '75-84 yrs'
    ]

tumor_site_options = [
    'Axillary tail',
    'Breast, NOS',
    'Central portion',
    'Lower-inner quadrant',
    'Lower-outer quadrant',
    'Nipple',
    'Overlapping lesion',
    'Upper-inner quadrant',
    'Upper-outer quadrant'
    ]

stage_options= ['I', 'II', 'III', 'IV']

def tabs():
    
    def select_button(button_name):
        st.session_state.selected_button = button_name

    # all tabs
    t1, t2, t3, t4 = st.columns([1,1,1,1])
    with t1:
        if st.button(
            'Demographics',
            key="Demographics",
            on_click=select_button,
            args=('Demographics',),
        ):
            st.session_state.page = 'Demographics'
            st.rerun()
    with t2:
        if st.button(
            'Tumor Characteristics',
            key="Tumor",
            on_click=select_button,
            args=('Tumor',),
        ):
            st.session_state.page = 'Tumor'
            st.rerun()
    with t3:
        if st.button(
            'Survival Analysis',
            key="Survival",
            on_click=select_button,
            args=('Survival',),
        ):
            st.session_state.page = 'Survival'
            st.rerun()
    with t4:
        if st.button(
            'Genome Analysis',
            key="Genome",
            on_click=select_button,
            args=('Genome',),
        ):
            st.session_state.page = 'Genome'
            st.rerun()
    if st.sidebar.button('Home'):
        st.session_state.page = 'Home'
        st.rerun()


def col_filter_options(df, col, remove = set()):
    remove = remove.union({'Unknown'})
    return ['All'] + sorted(list(set(df[col]) - remove))


@st.cache_data()
def load_data(path):
    return pd.read_csv(path+'.csv')