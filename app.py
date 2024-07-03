import fitz
import streamlit as st
from utils import *

st.set_page_config(layout="wide")

with st.sidebar:
    openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
    "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
    st.session_state.openai_api_key = openai_api_key
    # Add model selection in the sidebar
    model_options = ['gpt-4o', 'gpt-4-turbo', 'gpt-3.5-turbo']
    selected_model = st.sidebar.selectbox('Select a model', model_options, index=0)
    st.session_state['selected_model'] = selected_model

st.header('AI Coach: Resume customization', divider='violet')
st.caption('created by Education Victory')

# Initialize session state
for key, default_value in {
    'resume_analyzed': False,
    'resume_response': None,
    'company_product': None,
    'job_description': "",
    'active_tab': 0
}.items():
    if key not in st.session_state:
        st.session_state[key] = default_value

# Input for Company Name
st.write('Company Name (required)')
st.session_state.company_name = st.text_input(
    'Enter company name:',
    value=st.session_state.get('company_name', ''),  # Use the session state value if it exists
    max_chars=100,
    placeholder='Enter company name here...',
    label_visibility='collapsed'
)

st.write('Job Description (required)')
st.session_state.job_description = st.text_area(
    'Paste job description text:',
    value=st.session_state.job_description,  # Use the session state value if it exists
    max_chars=8500,
    height=300,
    placeholder='Paste job description text here...',
    label_visibility='collapsed'
)

resume_text = ''
if not st.session_state.resume_analyzed:
    file = st.file_uploader('Please upload your resume with PDF format.', type=['pdf'])
    if file is not None:
        with st.spinner('Extracting file text...'):
            try:
                # Open the uploaded PDF file
                with fitz.open(stream=file.read(), filetype='pdf') as pdf_document:
                    for page_num in range(len(pdf_document)):
                        page = pdf_document.load_page(page_num)
                        resume_text += page.get_text()
            except Exception as e:
                st.error(f"Error extracting text from PDF: {e}")
else:
    st.caption('Your resume has :blue[already] been analyzed. You can paste :blue[another] job description and then run the update again')

# Button to analyze resume
if not st.session_state.resume_analyzed:
    if st.button('Analyze Resume and Company', use_container_width=True):
        with st.spinner('Analyzing resume and company...'):
            resume_response = analyze_resume(resume_text)
            if resume_response:
                st.session_state.resume_analyzed = True
                st.session_state.resume_response = resume_response
                st.success('Resume analyzed successfully!')
            else:
                st.error("Failed to analyze your resume. Please try again.")
            company_product = get_company_product(st.session_state.company_name)
            if company_product:
                products_list = company_product['products']
                formatted_products = "\n\n".join(products_list)
                st.session_state['company_product'] = formatted_products
                st.success('Company product information retrieved successfully!')
            else:
                st.error("Failed to get company product information. Please try again.")

if st.session_state.resume_analyzed:
    st.header('Edit and Update', divider='violet')
    active_tab = st.session_state.active_tab
    tabs = st.tabs(['Skills', 'Experiences', 'Projects', 'Generate Projects'])

    tab_details = [
        ('Skills', 'skills', update_skill_prompt, Skill, skills_dict_to_string),
        ('Experiences', 'experiences', update_experience_prompt, Experience, experiences_list_to_string),
        ('Projects', 'projects', update_project_prompt, Project, projects_list_to_string),
        ('Genprojects', None, generate_project_prompt, Project, None)
    ]

    for i, (section_name, section_key, update_prompt, pydantic_object, data_to_string_func) in enumerate(tab_details):
        with tabs[i]:
            if active_tab == i:
                st.session_state.active_tab = i
            resume_response = st.session_state.resume_response
            original_data = resume_response.get(section_key, {}) if section_key else {}
            update_section(section_name, original_data, update_prompt, pydantic_object, data_to_string_func, i)
            display_results(section_name)
else:
    st.info('Please analyze your resume first to enable the tabs.')
