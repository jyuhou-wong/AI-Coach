import json
import fitz
import streamlit as st
from difflib import Differ
from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from prompt import analyze_resume_prompt, update_skill_prompt, update_experience_prompt, update_project_prompt, generate_project_prompt

model = ChatOpenAI(model='gpt-4o')
st.set_page_config(layout="wide")

class Resume(BaseModel):
    skills: Dict[str, List[str]] = Field(description='Dictionary of tech skills with categories as keys and lists of skills as values')
    experiences: List[Dict[str, Any]] = Field(description='List of work experience entries')
    projects: List[Dict[str, Any]] = Field(description='List of project entries')

class Skill(BaseModel):
    skills: Dict[str, List[str]] = Field(description='Dictionary of tech skills with categories as keys and lists of skills as values')

class Experience(BaseModel):
    company: str = Field(description="Name of the company")
    role: str = Field(description="Role in the company")
    details: List[str] = Field(description="List of details about the work experience")

class Project(BaseModel):
    name: str = Field(description="Name of the project")
    technologies: List[str] = Field(description="List of technologies used in the project")
    details: List[str] = Field(description="List of details about the project")

# Highlight changes function
def highlight_changes(original, new):
    def dict_to_str(d):
        if isinstance(d, dict):
            return json.dumps(d, indent=2)
        elif isinstance(d, list):
            return json.dumps(d, indent=2)
        return str(d)

    original_str = dict_to_str(original)
    new_str = dict_to_str(new)
    d = Differ()
    diff = d.compare(original_str.splitlines(), new_str.splitlines())
    highlighted = ''
    for line in diff:
        if line.startswith('+ '):
            highlighted += f'<span style="color: green; background-color: #e6ffe6">{line[2:]}</span><br>'
        elif line.startswith('- '):
            highlighted += f'<span style="color: red; background-color: #ffe6e6">{line[2:]}</span><br>'
    return highlighted

def skills_dict_to_string(skills_dict):
    skills_str = ''
    for category, skills in skills_dict.items():
        skills_str += f'{category}: {", ".join(skills)}\n'
    return skills_str.strip()

def experiences_list_to_string(experiences_list):
    experiences_str = ""
    for experience in experiences_list:
        company = experience.get('company', '')
        role = experience.get('role', '')
        details = experience.get('details', [])
        details_str = "\n    ".join(details)
        experiences_str += f"Company: {company}\nRole: {role}\nDetails:\n    {details_str}\n\n"
    return experiences_str.strip()

def projects_list_to_string(projects_list):
    projects_str = ""
    for project in projects_list:
        name = project.get('name', '')
        technologies = project.get('technologies', [])
        details = project.get('details', [])
        technologies_str = ", ".join(technologies)
        details_str = "\n    ".join(details)
        projects_str += f"Project Name: {name}\nTechnologies: {technologies_str}\nDetails:\n    {details_str}\n\n"
    return projects_str.strip()

def analyze_resume(resume_text):
    if not openai_api_key:
        st.error('Please enter your OpenAI API key.')
    elif not resume_text:
        st.error('Please provide your resume.')
    else:
        parser = JsonOutputParser(pydantic_object=Resume)
        prompt = PromptTemplate(
            template='{format_instructions}\n{query}\n',
            input_variables=['query'],
            partial_variables={'format_instructions': parser.get_format_instructions()},
        )
        chain = prompt | model | parser
        response = chain.invoke(
            {'query': 'given resume_text:\n' + resume_text + '\n' + analyze_resume_prompt})
        return response

def update_section(section_name, original_data, update_prompt, pydantic_object, data_to_string_func):
    st.subheader(f'Original {section_name}', divider='rainbow')
    original_data_str = data_to_string_func(original_data)
    st.text(original_data_str)
    st.subheader('Default Prompt', divider='rainbow')
    prompt_text = st.text_area('You can update the prompt based on your requirements', update_prompt, height=300)

    if st.button(f'Update {section_name}', use_container_width=True):
        with st.spinner(f'Updating {section_name} based on job description...'):
            parser = JsonOutputParser(pydantic_object=pydantic_object)
            prompt = PromptTemplate(
                template='{format_instructions}\n{query}\n',
                input_variables=['query'],
                partial_variables={'format_instructions': parser.get_format_instructions()},
            )
            chain = prompt | model | parser
            response = chain.invoke(
                {'query': f'given original {section_name.lower()}:\n' + original_data_str + '\nand job description:\n' + st.session_state.job_description + '\n' + prompt_text})
            if response:
                new_data = response.get(section_name.lower(), {})
                new_data_str = data_to_string_func(new_data)
                highlighted_data = highlight_changes(original_data_str, new_data_str)
                # Store results in session state
                st.session_state[f'{section_name.lower()}_new_data'] = new_data_str
                st.session_state[f'{section_name.lower()}_highlighted_data'] = highlighted_data

                st.subheader('Compare the differences', divider='rainbow')
                st.markdown(highlighted_data, unsafe_allow_html=True)
                st.subheader(f'New {section_name}', divider='rainbow')
                st.text(new_data_str)
                st.success(f'Update {section_name.lower()} successfully!')


def display_results(section_name):
    new_data_key = f'{section_name.lower()}_new_data'
    highlighted_data_key = f'{section_name.lower()}_highlighted_data'
    if new_data_key in st.session_state and highlighted_data_key in st.session_state:
        st.subheader('Compare the differences', divider='rainbow')
        st.markdown(st.session_state[highlighted_data_key], unsafe_allow_html=True)
        st.subheader(f'New {section_name}', divider='rainbow')
        st.text(st.session_state[new_data_key])
        st.success(f'Update {section_name.lower()} successfully!')


def invoke_chain(query, pydantic_object):
    parser = JsonOutputParser(pydantic_object=pydantic_object)
    prompt = PromptTemplate(
        template='{format_instructions}\n{query}\n',
        input_variables=['query'],
        partial_variables={'format_instructions': parser.get_format_instructions()},
    )
    chain = prompt | model | parser
    return chain.invoke({'query': query})

with st.sidebar:
    openai_api_key = st.text_input('OpenAI API Key', key='chatbot_api_key', type='password')
    '[Get an OpenAI API key](https://platform.openai.com/account/api-keys)'

st.header('AI Coach: Resume customization', divider='violet')
st.caption('created by Education Victory')

# Initialize session state
for key, default_value in {
    'resume_analyzed': False,
    'resume_response': None,
    'job_description': "",
    'active_tab': 0
}.items():
    if key not in st.session_state:
        st.session_state[key] = default_value

st.write('Job Description')
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
    if st.button('Analyze Resume', use_container_width=True):
        with st.spinner('Analyzing resume...'):
            resume_response = analyze_resume(resume_text)
            if resume_response:
                st.session_state.resume_analyzed = True
                st.session_state.resume_response = resume_response
                st.success('Resume analyzed successfully!')

if st.session_state.resume_analyzed:
    st.header('Edit and Update', divider='violet')
    active_tab = st.session_state.active_tab
    tabs = st.tabs(['Skills', 'Experiences', 'Projects', 'Generate Projects'])

    tab_details = [
        ('Skills', 'skills', update_skill_prompt, Skill, skills_dict_to_string),
        ('Experiences', 'experiences', update_experience_prompt, Experience, experiences_list_to_string),
        ('Projects', 'projects', update_project_prompt, Project, projects_list_to_string)
    ]

    for i, (section_name, section_key, update_prompt, pydantic_object, data_to_string_func) in enumerate(tab_details):
        with tabs[i]:
            if active_tab == i:
                st.session_state.active_tab = i
            resume_response = st.session_state.resume_response
            original_data = resume_response.get(section_key, {})
            update_section(section_name, original_data, update_prompt, pydantic_object, data_to_string_func)
            display_results(section_name)

    with tabs[3]:
        if active_tab == 3:
            st.session_state.active_tab = 3
        st.subheader('Generate Projects', divider='rainbow')
        st.subheader('Default Prompt', divider='rainbow')
        prompt_text = st.text_area('You can update the prompt based on your requirements', generate_project_prompt, height=300)
        if st.button('Generate Projects', use_container_width=True):
            with st.spinner('Generating projects based on job description...'):
                response = invoke_chain(
                    'job description:\n' + st.session_state.job_description + '\n' + generate_project_prompt, Project)
                if response:
                    new_projects = response.get('projects', [])
                    new_projects_str = projects_list_to_string(new_projects)
                    st.subheader('Generated Projects', divider='rainbow')
                    st.text(new_projects_str)
                    st.success('Projects generated successfully!')
else:
    st.info('Please analyze your resume first to enable the tabs.')
