from final_app_common import *
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

def tumor_characteristics():
    tabs()
    # Sidebar filters
    st.sidebar.title("Filters")
    print(st.session_state.active_tab)
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
    alluvial_data = load_data('laterality vs tumor site alluvial')
    alluvial_data = filter_df(alluvial_data)

    radar_data = load_data('age vs site radar data')
    radar_data = radar_data.melt(id_vars='age_group', var_name='tumor_site', value_name='count')
    radar_data = filter_df(radar_data)

    st.markdown("<div style='margin-top: 0px;'></div>", unsafe_allow_html=True)
    st.subheader("Laterality vs Tumor Site")
    if not alluvial_data.empty:
        labels = list(alluvial_data.laterality.unique()) + list(alluvial_data.tumor_site.unique())
        source = alluvial_data.laterality.apply(lambda x: list(alluvial_data.laterality.unique()).index(x))

        lateralityfig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=20,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=labels,
                color='rgba(200,200,200,0.8)'
            ),
            link=dict(
                source=source,
                target=alluvial_data['tumor_site'].apply(lambda x: len(alluvial_data.laterality.unique()) + list(alluvial_data.tumor_site.unique()).index(x)),
                value=alluvial_data['count'],
                color=[px.colors.qualitative.Pastel[i % len(px.colors.qualitative.Pastel)] for i in source],
            )
        )])
        lateralityfig.update_layout(
            title='',
            font_size=14,
            title_font_size=20,
            plot_bgcolor='white',
            margin=dict(l=60, r=60, t=30, b=30),
        )
        st.plotly_chart(lateralityfig, use_container_width=True)
    else:
        st.write("No data available for the selected filters.")
    
    st.subheader("Tumor Sites Across Age Groups")
    if not radar_data.empty:
        agefig = px.line_polar(
            radar_data,
            r='count',
            theta='tumor_site',
            color='age_group',
            line_close=True,
            title="",
        )
        agefig.update_traces(fill='toself')
        agefig.update_layout(
            margin=dict(l=50, r=50, t=50, b=50),
            polar=dict(
                angularaxis=dict(tickfont=dict(size=10))
            )
        )
        st.plotly_chart(agefig, use_container_width=True)
    else:
        st.write("No data available for the selected filters.")