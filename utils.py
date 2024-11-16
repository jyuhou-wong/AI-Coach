import json
import streamlit as st
from difflib import Differ
from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from prompt import *


class Resume(BaseModel):
    skills: Dict[str, List[str]] = Field(
        description="Dictionary of tech skills with categories as keys and lists of skills as values"
    )
    skills_original: str = Field(description="Original text for skills section")
    experiences: List[Dict[str, Any]] = Field(
        description="List of work experience entries"
    )
    experiences_original: str = Field(
        description="Original text for experiences section"
    )
    projects: List[Dict[str, Any]] = Field(description="List of project entries")
    projects_original: str = Field(description="Original text for projects section")


class Format(BaseModel):
    text: str = Field(description="New test with original format")


class Skill(BaseModel):
    skills: Dict[str, List[str]] = Field(
        description="Dictionary of tech skills with categories as keys and lists of skills as values"
    )


class Experience(BaseModel):
    company: str = Field(description="Name of the company")
    role: str = Field(description="Role in the company")
    details: List[str] = Field(description="List of details about the work experience")


class CompanyProduct(BaseModel):
    products: List[str] = Field(
        description="List of main products and services offered by the company, each as a single formatted string"
    )


class Project(BaseModel):
    name: str = Field(description="Name of the project")
    technologies: List[str] = Field(
        description="List of technologies used in the project"
    )
    details: List[str] = Field(description="List of details about the project")


def is_valid_json(json_str):
    try:
        json.loads(json_str)
        return True
    except ValueError:
        return False


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
        if line.startswith("+ "):
            highlighted += f'<span style="color: green; background-color: #e6ffe6">{line[2:]}</span><br>'
        elif line.startswith("- "):
            highlighted += f'<span style="color: red; background-color: #ffe6e6">{line[2:]}</span><br>'
        else:
            highlighted += f"{line[2:]}<br>"
    return highlighted


def skills_dict_to_string(skills_dict):
    skills_str = ""
    for category, skills in skills_dict.items():
        skills_str += f'{category}: {", ".join(skills)}\n'
    return skills_str.strip()


def experiences_list_to_string(experiences_list):
    experiences_str = ""
    for experience in experiences_list:
        company = experience.get("company", "")
        role = experience.get("role", "")
        details = experience.get("details", [])
        details_str = "\n    ".join(details)
        experiences_str += (
            f"Company: {company}\nRole: {role}\nDetails:\n    {details_str}\n\n"
        )
    return experiences_str.strip()


def projects_list_to_string(projects_list):
    projects_str = ""
    for project in projects_list:
        name = project.get("name", "")
        technologies = project.get("technologies", [])
        details = project.get("details", [])
        technologies_str = ", ".join(technologies)
        details_str = "\n    ".join(details)
        projects_str += f"Project Name: {name}\nTechnologies: {technologies_str}\nDetails:\n    {details_str}\n\n"
    return projects_str.strip()


def get_company_product(company_name):
    if not st.session_state.get("openai_api_key"):
        st.error("Please enter your OpenAI API key.")
        return

    selected_model = st.session_state.get("selected_model", "gpt-4")
    model = ChatOpenAI(
        model_name=selected_model,
        openai_api_key=st.session_state.openai_api_key,
        streaming=True,
    )
    parser = JsonOutputParser(pydantic_object=CompanyProduct)
    prompt = PromptTemplate(
        template="{format_instructions}\n{query}\n",
        input_variables=["query"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    query = f"Can you provide an overview of the main products and services offered by {company_name}? Please include details about their core features, target audience, and how these products serve the needs of professionals and businesses. If you don't know the {company_name}, just return an empty response"
    chain = prompt | model | parser
    try:
        response = chain.invoke({"query": query})
    except:
        st.error(
            f"The ChatGPT response sometimes didn't return a valid JSON. Please try update again."
        )
        return
    return response


def analyze_resume(resume_text):
    if not st.session_state.get("openai_api_key"):
        st.error("Please enter your OpenAI API key.")
        return
    if not resume_text:
        st.error("Please provide your resume.")
        return

    selected_model = st.session_state.get("selected_model", "gpt-4")
    model = ChatOpenAI(
        model_name=selected_model,
        openai_api_base=st.session_state.openai_api_base,
        openai_api_key=st.session_state.openai_api_key,
        streaming=True,
    )
    parser = JsonOutputParser(pydantic_object=Resume)
    prompt = PromptTemplate(
        template="{format_instructions}\n{query}\n",
        input_variables=["query"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    chain = prompt | model | parser
    try:
        response = chain.invoke(
            {
                "query": "given resume_text:\n"
                + resume_text
                + "\n"
                + analyze_resume_prompt
            }
        )
    except Exception as error:
        # st.error(
        #     f"The ChatGPT response sometimes didn't return a valid JSON. Please try update again."
        # )
        st.error(error)
        return
    return response


def update_section(
    section_name,
    company_name,
    job_description,
    original_data_str,
    update_prompt,
    pydantic_object,
    data_to_string_func,
    tab_index,
):
    if section_name == "Genprojects":
        company_product = get_company_product(company_name)
        if company_product:
            products_list = company_product["products"]
            formatted_products = "\n\n".join(products_list)
        else:
            formatted_products = ""
        update_prompt = (
            "Company Product: " + formatted_products + "\n\n" + update_prompt
        )
    prompt_text = update_prompt
    if st.button(f"Update {section_name}", type="primary", use_container_width=True):
        if not st.session_state.job_description or not st.session_state.company_name:
            st.error("Please provide company name and job description.")
            return
        st.session_state.active_tab = (
            tab_index  # Set the active tab in the session state
        )
        if not st.session_state.get("openai_api_key"):
            st.error("Please enter your OpenAI API key.")
            return

        selected_model = st.session_state.get("selected_model", "gpt-4")
        model = ChatOpenAI(
            model_name=selected_model,
            openai_api_base=st.session_state.openai_api_base,
            openai_api_key=st.session_state.openai_api_key,
            streaming=True,
        )
        parser = JsonOutputParser(pydantic_object=pydantic_object)
        prompt = PromptTemplate(
            template="{format_instructions}\n{query}\n",
            input_variables=["query"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        chain = prompt | model | parser
        try:
            response = chain.invoke(
                {
                    "query": f"given original {section_name.lower()}:\n"
                    + original_data_str
                    + "\nand job description:\n"
                    + job_description
                    + "\n"
                    + prompt_text
                }
            )
        except:
            st.error(
                f"The ChatGPT response sometimes didn't return a valid JSON. Please try update again."
            )
            return
        new_data = response.get(section_name.lower(), {})
        new_data_str = (
            data_to_string_func(new_data)
            if data_to_string_func
            else projects_list_to_string(new_data)
        )
        highlighted_data = highlight_changes(original_data_str, new_data_str)
        # Store results in session state
        st.session_state[f"{section_name.lower()}_new_data"] = new_data_str
        st.session_state[f"{section_name.lower()}_highlighted_data"] = highlighted_data


def display_results(section_name):
    new_data_key = f"{section_name.lower()}_new_data"
    highlighted_data_key = f"{section_name.lower()}_highlighted_data"
    if new_data_key in st.session_state and highlighted_data_key in st.session_state:
        st.subheader("Compare the differences", divider="rainbow")
        st.markdown(st.session_state[highlighted_data_key], unsafe_allow_html=True)
        st.subheader(f"New {section_name}", divider="rainbow")
        st.text(st.session_state[new_data_key])


def display_format(section_name):
    # Get the original and new data from session state
    new_data_key = f"{section_name.lower()}_new_data"
    if section_name == "Genprojects":
        original_data_key = "projects_original"
    else:
        original_data_key = f"{section_name.lower()}_original"
    if new_data_key in st.session_state:
        original_data = st.session_state.resume_response[original_data_key]
        new_data = st.session_state.get(f"{section_name.lower()}_new_data", "")

        selected_model = st.session_state.get("selected_model", "gpt-4")
        model = ChatOpenAI(
            model_name=selected_model,
            openai_api_base=st.session_state.openai_api_base,
            openai_api_key=st.session_state.openai_api_key,
            streaming=True,
        )
        parser = JsonOutputParser(pydantic_object=Format)
        prompt = PromptTemplate(
            template="{format_instructions}\n{query}\n",
            input_variables=["query"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        chain = prompt | model | parser

        # Prepare the query
        query = f"""
        Here is the original resume content:
        {original_data}

        Here is the new content for the {section_name} section:
        {new_data}

        Generate a text that corresponds to the original resume format using the new content. Looks like
        {{"text": ...}}
        """
        # Call LangChain with the prompt
        try:
            response = chain.invoke({"query": query})
        except:
            st.error(
                f"The ChatGPT response sometimes didn't return a valid JSON. Please try update again."
            )
            return
        response_str = json.dumps(response["text"])
        formatted_text = response_str.replace("\\n", "\n").replace("\\\\", "\\")
        formatted_text = formatted_text.strip('"')
        st.subheader("Formatted New " + section_name, divider="rainbow")
        st.text_area("Formatted Text", formatted_text, height=200)
        st.success(
            f"Update {section_name.lower()} successfully! You can click the button again to regenerate different versions."
        )
        st.info("You can also paste another Job Description and generate new result.")


def invoke_chain(query, pydantic_object):
    if not st.session_state.get("openai_api_key"):
        st.error("Please enter your OpenAI API key.")
        return

    selected_model = st.session_state.get("selected_model", "gpt-4")
    model = ChatOpenAI(
        model_name=selected_model,
        openai_api_base=st.session_state.openai_api_base,
        openai_api_key=st.session_state.openai_api_key,
        streaming=True,
    )
    parser = JsonOutputParser(pydantic_object=pydantic_object)
    prompt = PromptTemplate(
        template="{format_instructions}\n{query}\n",
        input_variables=["query"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    chain = prompt | model | parser
    try:
        response = chain.invoke({"query": query})
    except:
        st.error(
            f"The ChatGPT response sometimes didn't return a valid JSON. Please try update again."
        )
        return
    return response
