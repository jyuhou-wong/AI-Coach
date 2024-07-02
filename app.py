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
from prompt import analyze_resume_prompt, update_skill_prompt


model = ChatOpenAI(model="gpt-4o")

class Resume(BaseModel):
    skill: Dict[str, List[str]] = Field(description="Dictionary of tech skills with categories as keys and lists of skills as values")
    experience: List[Dict[str, Any]] = Field(description="List of work experience entries")
    projects: List[Dict[str, Any]] = Field(description="List of project entries")


class Skill(BaseModel):
    skill: Dict[str, List[str]] = Field(description="Dictionary of tech skills with categories as keys and lists of skills as values")


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
    highlighted = ""
    for line in diff:
        if line.startswith('+ '):
            highlighted += f"<span style='color: green; background-color: #e6ffe6'>{line[2:]}</span><br>"
        elif line.startswith('- '):
            highlighted += f"<span style='color: red; background-color: #ffe6e6'>{line[2:]}</span><br>"
        else:
            highlighted += f"{line[2:]}<br>"
    return highlighted

def skills_dict_to_string(skills_dict):
    skills_str = ""
    for category, skills in skills_dict.items():
        skills_str += f"{category}: {', '.join(skills)}\n"
    return skills_str.strip()


def analyze_resume(resume_text):
    if not openai_api_key:
        st.error("Please enter your OpenAI API key.")
    elif not resume_text:
        st.error("Please provide your resume.")
    else:
        parser = JsonOutputParser(pydantic_object=Resume)
        prompt = PromptTemplate(
            template="{format_instructions}\n{query}\n",
            input_variables=["query"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        chain = prompt | model | parser
        response = chain.invoke(
            {"query": 'given resume_text:\n' + resume_text + '\n' + analyze_resume_prompt})
        return response

with st.sidebar:
    openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
    "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"

st.header('AI Coach: Resume customization', divider='violet')
st.caption("created by Education Victory")

# Initialize session state variables
if 'resume_analyzed' not in st.session_state:
    st.session_state.resume_analyzed = False

st.write('Job Description')
job_description = st.text_area('Paste job description text:', max_chars=8500, height=300, placeholder='Paste job description text here...', label_visibility='collapsed')

resume_text = ""
if not st.session_state.resume_analyzed:
    file = st.file_uploader('Please upload your resume with PDF format.', type=['pdf'])
    if file is not None:
        with st.spinner("Extracting file text..."):
            # Open the uploaded PDF file
            with fitz.open(stream=file.read(), filetype="pdf") as pdf_document:
                for page_num in range(len(pdf_document)):
                    page = pdf_document.load_page(page_num)
                    resume_text += page.get_text()
else:
    st.caption("Your resume has :blue[already] been analyzed. You can paste :blue[another] job description and then run the update again")


# Button to analyze resume
if not st.session_state.resume_analyzed:
    if st.button("Analyze Resume", use_container_width=True):
        with st.spinner("Analyzing resume..."):
            resume_response = analyze_resume(resume_text)
            if resume_response:
                st.session_state.resume_analyzed = True
                st.session_state.resume_response = resume_response
                st.success("Resume analyzed successfully!")

if st.session_state.resume_analyzed:
    st.header('Edit and Update', divider='violet')
    tabs = st.tabs(["Skills", "Experiences", "Projects"])

    with tabs[0]:
        resume_response = st.session_state.resume_response
        original_skills = resume_response.get("skill", {})
        original_skills_str = skills_dict_to_string(original_skills)
        st.subheader('Original Skills', divider='rainbow')
        original_skill_area = st.text(original_skills_str)
        st.subheader('Default Prompt', divider='rainbow')
        update_skill_prompt = st.text_area('You can update the prompt based on your requirements', update_skill_prompt, height=300)

        if st.button("Update Skills", use_container_width=True):
            with st.spinner("Update Skills based on job description..."):
                parser = JsonOutputParser(pydantic_object=Skill)
                prompt = PromptTemplate(
                    template="{format_instructions}\n{query}\n",
                    input_variables=["query"],
                    partial_variables={"format_instructions": parser.get_format_instructions()},
                )
                chain = prompt | model | parser
                print(update_skill_prompt)
                response = chain.invoke(
                    {"query": 'given original tech skill:\n' + original_skills_str + '\nand job description:\n' + job_description + '\n'  + update_skill_prompt})
                if response:
                    new_skills = response.get("skill", {})
                    new_skills_str = skills_dict_to_string(new_skills)
                    highlighted_skills = highlight_changes(original_skills_str, new_skills_str)
                    st.subheader('Compare the differences', divider='rainbow')
                    st.markdown(highlighted_skills, unsafe_allow_html=True)
                    st.subheader('New Skills', divider='rainbow')
                    st.text(new_skills_str)
                    st.success("Update skills successfully!")

    with tabs[1]:
        st.header("New Experiences")
        update_experience_prompt = st.text_area("Update Experience Prompt:", "Your default experience prompt here")

        if st.button("Update Experiences"):
            # Add your logic to handle experience updates here
            pass

    with tabs[2]:
        st.header("New Projects")
        generate_project_prompt = st.text_area("Generate Project Prompt:", "Your default project prompt here")

        if st.button("Generate Projects"):
            # Add your logic to handle project generation here
            pass
else:
    st.info("Please analyze your resume first to enable the tabs.")
