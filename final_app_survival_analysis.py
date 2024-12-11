from final_app_common import *
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from lifelines import KaplanMeierFitter

def survival_analysis():
    tabs()
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

    # Create Tabs
    st.markdown("<div style='margin-top: 0px;'></div>", unsafe_allow_html=True)
        
    col1, col2 = st.columns([0.85, 0.15])

    with col1:
        st.subheader("Kaplan-Meier Survival Curves")

    with col2:
        # Display the info icon with a tooltip
        st.markdown("""
        <style>
        .tooltip {
            position: relative;
            display: inline-block;
            cursor: pointer;
            font-size: 24px; /* Size of the ℹ️ button */
        }

        .tooltip .tooltiptext {
            visibility: hidden;
            width: 300px; /* Increased width to fit larger text */
            background-color: #555;
            color: #fff;
            text-align: left; /* Left-align the text */
            border-radius: 6px;
            padding: 10px; /* Increased padding for better text spacing */
            font-size: 12px; /* Font size for the text inside */
            line-height: 1.4; /* Line height to reduce space between lines */
            white-space: normal; /* Ensures long text breaks properly */
            position: absolute;
            z-index: 1;
            bottom: 125%; /* Position the tooltip above the icon */
            left: 50%;
            margin-left: -150px; /* Center the tooltip relative to its parent */
            opacity: 0;
            transition: opacity 0.3s;
        }

        .tooltip:hover .tooltiptext {
            visibility: visible;
            opacity: 1;
        }
        </style>

        <div style="display: flex; align-items: center;">
            <span style="margin-right: 8px; font-size: 16px;">KM</span>
            <div class="tooltip">ℹ️
                <div class="tooltiptext">
                    Statistical method used to estimate how long people survive over time after a diagnosis or treatment. Handles censored data, which occurs when patients are lost to follow-up or the study ends before death.
                </div>
            </div>
            <span style="margin-right: 8px; margin-left: 15px; font-size: 16px;">ER/PR</span>
            <div class="tooltip">ℹ️
                <div class="tooltiptext">
                    ER (Estrogen Receptor) and PR (Progesterone Receptor) status indicate whether breast cancer cells have receptors for estrogen or progesterone hormones. If positive, the cancer may rely on these hormones to grow.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    col_map = {
        'Race/Ethnicity' : 'race',
        'Marital Status' : 'marital_status_at_diagnosis',
        'Stage' : 'adjusted_ajcc_6th_stage',
        'Laterality' : 'laterality',
        'Tumor Site' : 'tumor_site',
        'Tumor Size' : 'adjusted_ajcc_6th_t',
        'ER Status' : 'er_status',
        'PR Status' : 'pr_status',
    }

    gap, _ = st.columns([0.4, 0.6])
    with gap:
        chart_col = st.selectbox(
            "Survial Curve by:",
            ['Time (months)', 'Race/Ethnicity', 'Marital Status', 'Stage', 'Laterality', 'Tumor Site', 
            'Tumor Size', 'ER Status', 'PR Status'],
            help=""
        )

    survival_df = load_data('survival df')
    survival_df = survival_df.dropna()
    sdf = filter_df(survival_df)
    sdf.survival_months = sdf.survival_months.astype(int)

    # If there's no survival data after filtering, just skip
    if sdf.empty:
        st.write("No survival data available with current filters.")
    else:
        kmf = KaplanMeierFitter()
        if chart_col == 'Time (months)':
            kmf.fit(sdf.survival_months, event_observed=(sdf.vital_status == 'Dead'))
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=kmf.survival_function_.index,
                y=kmf.survival_function_['KM_estimate'],
                mode='lines',
                name='Survival Probability'
            ))
        else:
            fig = go.Figure()
            col = col_map[chart_col]
            for val in set(sdf[col].unique()) - {'Unknown', 'unknown', 0, '0'}:
                x = sdf[sdf[col] == val]
                kmf.fit(
                    x.survival_months, 
                    event_observed=(x.vital_status == 'Dead')
                )
                fig.add_trace(go.Scatter(
                    x=kmf.survival_function_.index,
                    y=kmf.survival_function_['KM_estimate'],
                    mode='lines',
                    name=val,
                    line=dict(width=2)
                ))
                fig.add_trace(go.Scatter(
                    x=list(kmf.confidence_interval_.index) + list(kmf.confidence_interval_.index[::-1]),
                    y=list(kmf.confidence_interval_['KM_estimate_lower_0.95']) + 
                    list(kmf.confidence_interval_['KM_estimate_upper_0.95'][::-1]),
                    fill='toself',
                    fillcolor='rgba(0,100,250,0.07)',
                    line=dict(width=0),
                    hoverinfo="skip",
                    showlegend=False,
                ))

        fig.update_layout(
            title='Kaplan-Meier Survival Curve by ' + chart_col,
            xaxis_title='Survival Time (Months)',
            yaxis_title='Survival Probability',
            template='plotly_white',
            hovermode='x unified',
            legend_title=chart_col,
            height=600
        )
        st.plotly_chart(fig, use_container_width=True)
