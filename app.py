import re
import fitz
import streamlit as st
from utils import *
from docx import Document
from pylatexenc.latex2text import LatexNodes2Text

st.set_page_config(layout="wide")

with st.sidebar:
    openai_api_base = st.text_input(
        "OpenAI API Base", key="chatbot_api_base", value="https://api.openai.com/v1"
    )
    openai_api_key = st.text_input(
        "OpenAI API Key", key="chatbot_api_key", type="password"
    )
    "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
    st.session_state.openai_api_base = openai_api_base
    st.session_state.openai_api_key = openai_api_key
    # Add model selection in the sidebar
    model_options = ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]
    selected_model = st.sidebar.selectbox("Select a model", model_options, index=0)
    st.session_state["selected_model"] = selected_model

st.header("AI Coach: Resume customization", divider="violet")
st.caption("created by Education Victory")

# Initialize session state
for key, default_value in {
    "resume_analyzed": False,
    "resume_response": None,
    "company_name": "",
    "resume_text": "",
    "job_description": "",
    "file_type": "",
    "active_tab": 0,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default_value

st.subheader("1. Upload and Analyze Resume")
file = st.file_uploader(
    "Please upload your resume in PDF, DOCX, or LaTeX format.",
    type=["pdf", "docx", "tex"],
    disabled=st.session_state.resume_analyzed,
)
if file:
    with st.spinner("Extracting file text..."):
        try:
            if file.type == "application/pdf":
                # Open the uploaded PDF file
                with fitz.open(stream=file.read(), filetype="pdf") as pdf_document:
                    for page_num in range(len(pdf_document)):
                        page = pdf_document.load_page(page_num)
                        st.session_state.resume_text += page.get_text()
                    st.session_state.file_type = "PDF"
            elif (
                file.type
                == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            ):
                # Open the uploaded DOCX file
                doc = Document(file)
                for para in doc.paragraphs:
                    st.session_state.resume_text += para.text + "\n"
                st.session_state.file_type = "DOC"
            elif file.type == "application/x-tex" or (
                file.type == "application/octet-stream" and file.name.endswith(".tex")
            ):
                # Open the uploaded LaTeX file
                st.session_state.resume_text = file.read().decode("utf-8")
                st.session_state.file_type = "Latex"
        except Exception as e:
            st.error(f"Error extracting text from file: {e}")

if st.button(
    "Analyze Resume",
    use_container_width=True,
    type="primary",
    disabled=st.session_state.resume_analyzed,
):
    with st.spinner("Analyzing resume..."):
        resume_response = analyze_resume(st.session_state.resume_text)
        if resume_response:
            st.session_state.resume_analyzed = True
            st.session_state.resume_response = resume_response
            st.rerun()
        else:
            st.error("Failed to analyze your resume. Please try again.")

if st.session_state.resume_analyzed:
    st.success("Resume analyzed successfully!")
    tabs = st.tabs(["Skills", "Experiences", "Projects"])
    tab_details = [
        ("Skills", "skills", skills_dict_to_string),
        ("Experiences", "experiences", experiences_list_to_string),
        ("Projects", "projects", projects_list_to_string),
    ]
    for i, (section_name, section_key, data_to_string_func) in enumerate(tab_details):
        with tabs[i]:
            original_data = (
                st.session_state.resume_response.get(section_key, {})
                if section_key
                else {}
            )
            st.subheader(f"{section_name}", divider="rainbow")
            original_data_str = data_to_string_func(original_data)
            st.text(original_data_str)

st.write("")

st.subheader("2. Enter company name and job description")
# Input for Company Name
st.write("Company Name (required)")
st.session_state.company_name = st.text_input(
    "Enter company name:",
    value=st.session_state.get(
        "company_name", ""
    ),  # Use the session state value if it exists
    max_chars=100,
    placeholder="Enter company name here...",
    label_visibility="collapsed",
    disabled=not st.session_state.resume_analyzed,
)
st.info("We will generate new projects based on the products of the company")

st.write("Job Description (required)")
st.session_state.job_description = st.text_area(
    "Paste job description text:",
    value=st.session_state.job_description,  # Use the session state value if it exists
    max_chars=12000,
    height=300,
    placeholder="Paste job description text here...",
    label_visibility="collapsed",
    disabled=not st.session_state.resume_analyzed,
)

if st.session_state.resume_analyzed:
    st.header("3. Resume customization", divider="violet")
    active_tab = st.session_state.active_tab
    tabs = st.tabs(["Skills", "Experiences", "Projects", "Generate Projects"])
    tab_details = [
        ("Skills", "skills", update_skill_prompt, Skill, skills_dict_to_string),
        (
            "Experiences",
            "experiences",
            update_experience_prompt,
            Experience,
            experiences_list_to_string,
        ),
        (
            "Projects",
            "projects",
            update_project_prompt,
            Project,
            projects_list_to_string,
        ),
        ("Genprojects", None, generate_project_prompt, Project, None),
    ]
    for i, (
        section_name,
        section_key,
        update_prompt,
        pydantic_object,
        data_to_string_func,
    ) in enumerate(tab_details):
        with tabs[i]:
            if active_tab == i:
                st.session_state.active_tab = i
            resume_response = st.session_state.resume_response
            original_data = resume_response.get(section_key, {}) if section_key else {}
            st.subheader("Default Prompt", divider="rainbow")
            prompt_text = st.text_area(
                "You can update the prompt based on your requirements",
                update_prompt,
                height=300,
            )
            original_data = resume_response.get(section_key, {}) if section_key else {}
            if section_name != "Genprojects":
                original_data_str = data_to_string_func(original_data)
            else:
                original_data_str = ""
            with st.spinner("Generating data..."):
                update_section(
                    section_name,
                    st.session_state.company_name,
                    st.session_state.job_description,
                    original_data_str,
                    prompt_text,
                    pydantic_object,
                    data_to_string_func,
                    i,
                )
                display_results(section_name)
            with st.spinner("Generateing formatted data..."):
                display_format(section_name)
else:
    st.warning("Please analyze resume before resume customization.")
