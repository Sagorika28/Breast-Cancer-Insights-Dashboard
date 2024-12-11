from final_app_common import *
import streamlit as st
import plotly.express as px

def demographics():
    tabs()
    st.sidebar.title("Filters")
    year_range = st.sidebar.slider("Year Range", min_value=min_year, max_value=max_year, value=(min_year, max_year))
    age_groups_selected = st.sidebar.multiselect("Age Groups", age_group_options)
    tumor_sites_selected = st.sidebar.multiselect("Tumor Site", tumor_site_options)
    stage_selected = st.sidebar.multiselect("Stage", stage_options)

    # Apply filters
    def filter_df(df):
        if 'year_of_diagnosis' in df.columns:
            df = df[
                (df["year_of_diagnosis"] >= year_range[0]) &
                (df["year_of_diagnosis"] <= year_range[1])
            ]
        if 'age_group' in df.columns and age_groups_selected:
            df = df[df["age_group"].isin(age_groups_selected)]
        if 'tumor_site' in df.columns and tumor_sites_selected:
            df = df[df["tumor_site"].isin(tumor_sites_selected)]
        if 'adjusted_ajcc_6th_stage' in df.columns and stage_selected:
            df = df[df["adjusted_ajcc_6th_stage"].isin(stage_selected)]
        return df

    # filter all dfs
    demographics_df = load_data('patients by year and age')
    demographics_df.year_of_diagnosis = demographics_df.year_of_diagnosis.astype(int)
    demographics_df.age_group = demographics_df.age_group.astype(str)
    demographics_df = filter_df(demographics_df)

    # Create Tabs
    st.markdown("<div style='margin-top: 0px;'></div>", unsafe_allow_html=True)
    st.session_state.active_tab = 'Demographics'
    st.subheader("Number of Patients by Year and Age Group")
    print(demographics_df.head())
    df1 = demographics_df.groupby(['year_of_diagnosis', 'age_group'])['Age'].sum().reset_index()
    print(df1.head())
    print(df1.shape)
    df1 = df1.rename(columns = {'Age' : 'Number of Patients', 'year_of_diagnosis' : 'Year of Diagnosis', 'age_group' : 'Age Group'})
    if not df1.empty:
        fig1 = px.line(
            df1,
            x='Year of Diagnosis',
            y='Number of Patients',
            color='Age Group',
            title='',
            color_discrete_sequence=px.colors.qualitative.T10,
            height=600
        )
        fig1.update_layout(yaxis=dict(tickmode='auto',  nticks=15))
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.write("No data available for the selected filters.")