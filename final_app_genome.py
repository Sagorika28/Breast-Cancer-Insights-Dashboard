from final_app_common import *
import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from io import StringIO
from sklearn.cluster import KMeans
from sklearn.preprocessing import LabelEncoder, StandardScaler
from scipy.stats import mode


clustering_features = ['age_at_diagnosis', 'Cancer Stage Encoded', 'Site Encoded']
num_clusters = 50
exclude_diag = ["Not Reported", "Tubular adenocarcinoma", "Basal cell carcinoma, NOS", 
                "Phyllodes tumor, malignant", "Large cell neuroendocrine carcinoma", "Pleomorphic carcinoma","Carcinoma, NOS"]
exclude_n = ["Unknown","nan","N1c","N0 (mol+)","N3c"]
exclude_m = ["Unknown","nan"]
exclude_t = ["Unknown","nan","T4d","T2b","T3a","T2a"]



def genome_dashboard():
    tabs()
    clusterdata = load_data('genome_cluster')
    st.sidebar.title("Filters")
    # Gene filter (no exclusion here)
    unique_genes = sorted(clusterdata['Gene'].unique())
    selected_genes = st.sidebar.multiselect("Select Genes:", options=unique_genes, default=[])
    # Cancer Stage filter
    unique_stages = sorted(clusterdata['Cancer Stage'].dropna().unique())
    selected_stages = st.sidebar.multiselect("Select Cancer Stages:", options=unique_stages, default=[])

    # Pathologic N filter
    unique_n = sorted([x for x in clusterdata['ajcc_pathologic_n'].dropna().unique() if x not in exclude_n])
    selected_n = st.sidebar.multiselect("Select Pathologic N Stages:", options=unique_n, default=[])

    # Pathologic M filter
    unique_m = sorted([x for x in clusterdata['ajcc_pathologic_m'].dropna().unique() if x not in exclude_m])
    selected_m = st.sidebar.multiselect("Select Pathologic M Stages:", options=unique_m, default=[])

    # Pathologic T filter
    unique_t = sorted([x for x in clusterdata['ajcc_pathologic_t'].dropna().unique() if x not in exclude_t])
    selected_t = st.sidebar.multiselect("Select Pathologic T Stages:", options=unique_t, default=[])

    # Primary Diagnosis filter
    unique_diag = sorted([d for d in clusterdata['primary_diagnosis'].dropna().unique() if d not in exclude_diag])
    selected_diag = st.sidebar.multiselect("Select Primary Diagnoses:", options=unique_diag, default=[])

    # Expression slider using FULL range of clusterdata (default view)
    min_expr, max_expr = float(clusterdata['Expression'].min()), float(clusterdata['Expression'].max())
    expression_range = st.sidebar.slider(
        "Select Expression Level Range:",
        min_value=min_expr,
        max_value=max_expr,
        value=(min_expr, max_expr)
    )

    # Apply filters to clusterdata
    filtered_cluster = clusterdata.copy()

    if selected_genes:
        filtered_cluster = filtered_cluster[filtered_cluster['Gene'].isin(selected_genes)]
    if selected_stages:
        filtered_cluster = filtered_cluster[filtered_cluster['Cancer Stage'].isin(selected_stages)]
    if selected_n:
        filtered_cluster = filtered_cluster[filtered_cluster['ajcc_pathologic_n'].isin(selected_n)]
    else:
        # Always exclude the undesired N categories
        filtered_cluster = filtered_cluster[~filtered_cluster['ajcc_pathologic_n'].isin(exclude_n)]

    if selected_m:
        filtered_cluster = filtered_cluster[filtered_cluster['ajcc_pathologic_m'].isin(selected_m)]
    else:
        # Exclude unwanted M categories
        filtered_cluster = filtered_cluster[~filtered_cluster['ajcc_pathologic_m'].isin(exclude_m)]

    if selected_t:
        filtered_cluster = filtered_cluster[filtered_cluster['ajcc_pathologic_t'].isin(selected_t)]
    else:
        # Exclude unwanted T categories
        filtered_cluster = filtered_cluster[~filtered_cluster['ajcc_pathologic_t'].isin(exclude_t)]

    if selected_diag:
        filtered_cluster = filtered_cluster[filtered_cluster['primary_diagnosis'].isin(selected_diag)]
    else:
        # Exclude unwanted diagnoses
        filtered_cluster = filtered_cluster[~filtered_cluster['primary_diagnosis'].isin(exclude_diag)]

    filtered_cluster = filtered_cluster[
        (filtered_cluster['Expression'] >= expression_range[0]) & (filtered_cluster['Expression'] <= expression_range[1])
    ]

    # Heatmap data
    if not filtered_cluster.empty:
        cluster_aggregated = filtered_cluster.groupby('Cluster').agg({'Cancer Stage': lambda x: x.mode()[0]}).reset_index()
        heatmap_data = filtered_cluster.pivot_table(
            index='Cluster',
            columns='Gene',
            values='Expression',
            aggfunc='mean'
        )
        if not heatmap_data.empty:
            heatmap_customdata = cluster_aggregated.set_index('Cluster').loc[heatmap_data.index, 'Cancer Stage'].values
        else:
            heatmap_data = pd.DataFrame()
            heatmap_customdata = []
    else:
        heatmap_data = pd.DataFrame()
        heatmap_customdata = []

    st.markdown("### Heatmap of Mean Gene Expression Levels")
    if not heatmap_data.empty:
        fig_heatmap = px.imshow(
            heatmap_data.values,
            labels=dict(x="Gene", y="Cluster", color="Expression Level"),
            x=heatmap_data.columns,
            y=heatmap_data.index,
            color_continuous_scale='Blues',
            title=''#f"Heatmap of Mean Gene Expression Levels ({num_clusters} Clusters)"
        )
        fig_heatmap.update_traces(
            hovertemplate=(
                "Gene: %{x}<br>"
                "Cluster: %{y}<br>"
                "Expression: %{z:.2f}<br>"
                # "Cancer Stage: %{customdata}"
            ),
            customdata=heatmap_customdata
        )
        fig_heatmap.update_layout(width=1200, height=600)
        st.plotly_chart(fig_heatmap, use_container_width=True)
    else:
        st.write("No data available for the selected filters to display a heatmap.")

    # Aggregate for other plots
    if not filtered_cluster.empty:
        aggregated_data = filtered_cluster.groupby(
            ['Case', 'Cancer Stage', 'ajcc_pathologic_n', 'ajcc_pathologic_m', 'ajcc_pathologic_t', 'ajcc_pathologic_stage', 'primary_diagnosis'],
            as_index=False
        ).agg({'Expression': 'mean'})
    else:
        aggregated_data = pd.DataFrame()

    st.markdown("### Distribution of Cases by AJCC Pathologic Stage")
    if not aggregated_data.empty and 'ajcc_pathologic_stage' in aggregated_data.columns:
        filtered_stage_data = aggregated_data[aggregated_data['ajcc_pathologic_stage'] != "Unknown"]
        if not filtered_stage_data.empty:
            stage_counts = filtered_stage_data['Cancer Stage'].value_counts().sort_index()
            plot_data = stage_counts.reset_index()
            plot_data.columns = ['Cancer Stage', 'Number of Cases']
            fig_bar = px.bar(
                plot_data,
                x='Cancer Stage',
                y='Number of Cases',
                text='Number of Cases',
                title='',#'Distribution of Cases by AJCC Pathologic Stage',
                labels={'Cancer Stage': 'AJCC Pathologic Stage', 'Number of Cases': 'Number of Cases'},
            )
            fig_bar.update_traces(textposition='outside', marker_color='lightblue', marker_line_color='black', marker_line_width=1)
            fig_bar.update_layout(xaxis_tickangle=45)
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.write("No data available for the selected filters.")
    else:
        st.write("No data available for the selected filters.")

    st.markdown(
        """
        <div style="display: flex; align-items: center;">
            <h3 style="margin: 0;">Average Gene Expression Across Pathologic N Stages</h3>
            <div style="margin-left: 10px;" class="tooltip">ℹ️
                <span class="tooltiptext">
                    AJCC Pathologic N stage indicates the extent of regional lymph node involvement. N followed by a number 0 to 3 indicates whether the cancer has spread to lymph nodes near the breast and, if so, how many lymph nodes are involved. As the value of the number after the N increases, so does the tumor size and spread.
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    if not aggregated_data.empty and 'ajcc_pathologic_n' in aggregated_data.columns:
        if not aggregated_data.empty:
            fig_box_n = px.box(
                aggregated_data,
                x='ajcc_pathologic_n',
                y='Expression',
                color='ajcc_pathologic_n',
                title='',#"Average Gene Expression Across Selected Pathologic N Stages",
                labels={'ajcc_pathologic_n': 'AJCC Pathologic N Stage', 'Expression': 'Expression Level'},
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_box_n.update_layout(xaxis_tickangle=45, showlegend=False)
            st.plotly_chart(fig_box_n, use_container_width=True)
        else:
            st.write("No data available for the selected filters.")
    else:
        st.write("No data available for the selected filters.")

    st.markdown(
    """
    <div style="display: flex; align-items: center;">
        <h3 style="margin: 0;">Average Gene Expression Across Pathologic M Stages</h3>
        <div style="margin-left: 10px;" class="tooltip">ℹ️
            <span class="tooltiptext">
                AJCC Pathologic M stage indicates whether there is distant metastasis or spread of cancer to other parts of the body. M followed by a 0 or 1 indicates whether the cancer has spread to distant organs. For 0, no distant spread has been found on x-rays or by physical exam. For 1, cancer has spread to distant organs.
            </span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
    )
    if not aggregated_data.empty and 'ajcc_pathologic_m' in aggregated_data.columns:
        fig_box_m = px.box(
            aggregated_data,
            x='ajcc_pathologic_m',
            y='Expression',
            color='ajcc_pathologic_m',
            title='',#"Average Gene Expression Across Selected Pathologic M Stages",
            labels={'ajcc_pathologic_m': 'AJCC Pathologic M Stage', 'Expression': 'Expression Level'},
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_box_m.update_layout(xaxis_tickangle=45, showlegend=False)
        st.plotly_chart(fig_box_m, use_container_width=True)
    else:
        st.write("No data available for the selected filters.")

    st.markdown(
        """
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
            <h3 style="margin: 0;">Average Gene Expression Across Pathologic T Stages</h3>
            <div style="margin-left: 10px;" class="tooltip">ℹ️
                <span class="tooltiptext">
                    AJCC Pathologic T stage indicates the size and extent of the primary tumor. T followed by a number 0 to 4 describes the primary tumor’s size and if it has spread to the skin or to the chest wall under the breast. As the value of the number after the T increases, so does the tumor size and spread.
                </span>
            </div>
        </div>
        """,
    unsafe_allow_html=True
    )
    if not aggregated_data.empty and 'ajcc_pathologic_t' in aggregated_data.columns:
        fig_box_t = px.box(
            aggregated_data,
            x='ajcc_pathologic_t',
            y='Expression',
            color='ajcc_pathologic_t',
            title='',#"Average Gene Expression Across Selected Pathologic T Stages",
            labels={'ajcc_pathologic_t': 'AJCC Pathologic T Stage', 'Expression': 'Expression Level'},
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_box_t.update_layout(xaxis_tickangle=45, showlegend=False)
        st.plotly_chart(fig_box_t, use_container_width=True)
    else:
        st.write("No data available for the selected filters.")

    st.markdown("### Gene Expression Distribution Across Primary Diagnosis")
    if not aggregated_data.empty and 'primary_diagnosis' in aggregated_data.columns:
        filtered_diag = aggregated_data.copy()
        if not filtered_diag.empty:
            filtered_diag['primary_diagnosis'] = filtered_diag['primary_diagnosis'].apply(
                lambda x: '<br>'.join(x.split(' ', 3)[:3]) if len(x.split(' ')) > 3 else x.replace(' ', '<br>')
            )
            fig_violin = px.violin(
                filtered_diag,
                x='primary_diagnosis',
                y='Expression',
                box=True,
                points=False,
                color='primary_diagnosis',
                title='',#"Gene Expression Distribution Across Selected Primary Diagnoses",
                labels={'primary_diagnosis': 'Primary Diagnosis', 'Expression': 'Expression Level'},
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            fig_violin.update_layout(xaxis_tickangle=0, showlegend=False, width=1200, height=700)
            st.plotly_chart(fig_violin, use_container_width=True)
        else:
            st.write("No data available for the selected filters.")
    else:
        st.write("No data available for the selected filters.")
