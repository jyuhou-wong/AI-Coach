analyze_resume_prompt = """requirements:
1. Format the output as JSON objects for each tech skill section, work experience, and project, with sections containing lists of items.
2. Bullet points in the work experience and projects sections should be nested within lists.

Action:
1. Return three items of data: the tech skill, work experience, and projects in the resume text. Here is an example:

Output format:
{
  "skill": {
    "Programming Languages": ["Java", "Python"],
    "Frameworks and Tools": ["Spring", "Kubernetes"],
    "Databases": ["MySQL"],
    "Cloud services": ["AWS EC2", "AWS S3"]
  },
  "experience": [
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
2. The updated tech skill should contain no more than 4 sections, section can only choose from Programming languages, Frameworks and Tools, Databases, Cloud services (Choose from AWS, GCP, Azure, Oracle Cloud)
3. Do not include a section in the output if it has no items.

Action:
1. Update the tech skill in the resume based on the keywords in the job description, here is an example output:

{
  "skill": {
    "Programming Languages": ["Java", "Python"],
    "Frameworks and Tools": ["Spring", "Kubernetes"],
    "Databases": ["MySQL"],
    "Cloud services": ["AWS EC2", "AWS S3"]
  }
"""
