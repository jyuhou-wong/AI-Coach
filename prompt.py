analyze_resume_prompt = """Requirements:
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
        "Implemented a Vite-based build system using Django and React, reducing build times by 40% and improving overall application performance."
      ]
    }
  ],
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

update_skill_prompt = """Requirements:
1. The updated tech skill should contain no more than 4 sections, which can only be: Programming Languages, Frameworks and Tools, Databases, and Cloud Services (Choose from AWS, GCP, Azure, Oracle Cloud).
2. Every section should have 4 to 8 skills
3. Ensure that all important skills mentioned in the job description are included in the relevant sections.
4. Format the output as JSON objects for each tech skill section with sections containing lists of items.
5. Do not include a section in the output if it has no items.
6. Do not delete important skills or certifications.

Action:
1. Rewrite the tech skills in the resume based on the requirements in the job description. Here is an example output:

{
  "skills": {
    "Programming Languages": ["Java", "Python", ...],
    "Frameworks and Tools": ["Spring", "Kubernetes", ...],
    "Databases": ["MySQL", ...],
    "Cloud Services": ["AWS EC2", "AWS S3", ...]
  }
}
"""

update_experience_prompt = """Requirements:
1. Do not add extra experience; use the keywords in the job description.
2. Use a professional and concise style, with 5 bullet points.
3. Every bullet point should include at least one tech skill
4. Do not change the words if they have the same or similar meaning.
5. Format the output as JSON objects for each work experience with company name, role, and details.
6. Ensure each updated bullet point is at least as long as the original bullet point.

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

update_project_prompt = """Requirements:
1. Use a professional and concise style, with 3 bullet points.
2. Every bullet point should include at least one tech skill
3. Every bullet point should not shorter than original version
4. Generate bullet points that describe [your accomplishment or task], using [specific method or technology], and highlight [specific outcome or benefit, including any quantifiable improvements].
5. Add example numbers and metrics in the experience and projects like reducing 50% API request time to make it more impressive.
6. Format the output as JSON objects for each project with the project name, technologies used, and details.
7. Ensure each updated bullet point is at least as long as the original bullet point.

Action:
1. Update the details of my original projects to meet the requirements in the job description to improve my chances of getting an interview.

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

generate_project_prompt = """Requirements:
1. Use a professional and concise style.
2. Every project should have 3 bullet points, each bullet point should include at least one tech skill.
3. Generate bullet points that describe [your accomplishment or task], using [specific method or technology], and highlight [specific outcome or benefit, including any quantifiable improvements].
4. These projects should have a certain degree of differentiation, and each can meet the specific requirements of the position.
5. The project name should be creative and not too common, using the tech stack list in the job description.
6. Add example numbers and metrics in the experience and projects like reducing 50% API request time to make it more impressive.
7. Format the output as JSON objects for each project with the project name, technologies used, and details.

Action:
1. Generate 3 projects based on the job description and similar to the company products. Here is an example output:

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
