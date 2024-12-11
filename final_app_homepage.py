import streamlit as st
from streamlit_lottie import st_lottie
import json

def load_lottie_file(filepath):
    with open(filepath, "r") as f:
        return json.load(f)

def homepage():
    lottie_cancer_animation = load_lottie_file("lottie.json")
    
    with st.container():
        col1, col2 = st.columns([2, 3])

        with col1:
            st.title("Breast Cancer Insights")
            st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
            st.markdown(
            """
            <div style="text-align: justify;">
                The Breast Cancer Insights Dashboard brings together gene and clinical data with interactive features to help you create insights about breast cancer pathology. 
                Dive into the data and uncover meaningful insights to make informed decisions.
            </div>
            """,
            unsafe_allow_html=True,
            )

            st.markdown("<div style='margin-top: 80px;'></div>", unsafe_allow_html=True)
            st.markdown(
            """
            <div style="text-align: justify;">
                Project Team Members: Sarah Innis, Arjita Nema, Sagorika Ghosh, Aaditya Chopra, Jay Sanghavi
            </div>
            """,
            unsafe_allow_html=True,
            )

            st.markdown("<div style='margin-top: 90px;'></div>", unsafe_allow_html=True)
            # Add custom CSS for button hover effect
            st.markdown(
                """
                <style>
                .stButton>button:hover {
                    color: pink !important;
                    background-color: transparent !important;
                    border: 2px solid pink !important;
                }
                </style>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Go to Dashboard"):
                st.session_state.page = 'Dashboard'
                st.rerun()

        with col2:
            if lottie_cancer_animation:
                st_lottie(lottie_cancer_animation, height=500)
            else:
                st.error("Error loading animation. Please check the file.")
