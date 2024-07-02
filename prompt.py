analyze_resume_prompt = """requirements:
1. Format the output as JSON objects for each tech skill section, work experience, and project, with sections containing lists of items.
2. Bullet points in the work experience and projects sections should be nested within lists.

Action:
1. Return three items of data: the tech skill, work experience, and projects in the resume text. Here is an example:

Output format:
{
  "skills": {
    "Programming Languages": ["Java", "Python"],
    "Frameworks and Tools": ["Spring", "Kubernetes"],
    "Databases": ["MySQL"],
    "Cloud services": ["AWS EC2", "AWS S3"]
  },
  "experiences": [
    {
      "company": "ABC Corp",
      "role": "Software Developer",
      "details": [
        "Developed RESTful APIs using Java and Spring",
        "Improved database performance with MySQL optimizations"
      ]
    }
  ],
  "projects": [
    {
      "name": "Inventory Management System",
      "technologies": ["Python", "Django"],
      "details": [
        "Created a web application for managing inventory",
        "Implemented user authentication and session management"
      ]
    }
  ]
}
"""

update_skill_prompt = """requirements:
1. Format the output as JSON objects for each tech skill section with sections containing lists of items.
2. The updated tech skill should contain no more than 4 sections, the section can only choose from Programming languages, Frameworks and Tools, Databases, and Cloud services (Choose from AWS, GCP, Azure, Oracle Cloud)
3. Do not include a section in the output if it has no items.

Action:
1. Update the tech skill in the resume based on the keywords in the job description, here is an example output:

{
  "skills": {
    "Programming Languages": ["Java", "Python"],
    "Frameworks and Tools": ["Spring", "Kubernetes"],
    "Databases": ["MySQL"],
    "Cloud services": ["AWS EC2", "AWS S3"]
  }
"""

update_experience_prompt = """requirements:
1. Format the output as JSON objects for each work experience with company name, role, and details.
2. Do not add extra experience, try to use the keyword in the job description.
3. Professional and concise style use normal English, with 5 bullet points (between 15 to 20 words), every bullet point should include at least one tech skill
4. Do not change the words if they have the same or similar meaning

Action:
1. Update the details of the original work experience in the resume to match the requirements in the job description. Here is an example output:

{
  "experiences": [
    {
      "company": "ABC Corp",
      "role": "Software Developer",
      "details": [
        "Implemented a Vite-based build system using Django and React, reducing build times by 40% and improving overall application performance.",
      ]
    }
  ]
}
"""

update_project_prompt = """requirements:
1. Format the output as JSON objects for each project with the project name, technologies used, and details.
2. Professional and concise style use normal English, with 5 bullet points (between 15 to 20 words), every bullet point should include at least one tech skill
3. Add example numbers and metrics in the experience and projects like reducing 50% API request time to make it more impressive

Action:
1. Update the details of original projects in the resume to match the requirements in the job description. Here is an example output:

{
  "projects": [
    {
      "name": "Inventory Management System",
      "technologies": ["Python", "Django"],
      "details": [
        "Implemented a Vite-based build system using Django and React, reducing build times by 40% and improving overall application performance.",
      ]
    }
  ]
}
"""

generate_project_prompt = """requirements:
1. Format the output as JSON objects for each project with the project name, technologies used, and details.
2. Do not include a project if it has no details.
3. These projects should have a certain degree of differentiation, and each can meet the specific requirements of the position requirements.
4. The Project name should be creative and not too common, use the tech stack list in the job description
5. Professional and concise style use normal English, with 5 bullet points (between 15 to 20 words), every bullet point should include at least one tech skill
6. Add example numbers and metrics in the experience and projects like reducing 50% API request time to make it more impressive

Action:
1. Generate 3 projects based on the keywords in the job description. Here is an example output:

{
  "genprojects": [
    {
      "name": "Inventory Management System",
      "technologies": ["Python", "Django"],
      "details": [
        "Implemented a Vite-based build system using Django and React, reducing build times by 40% and improving overall application performance.",
      ]
    }
  ]
}
"""
