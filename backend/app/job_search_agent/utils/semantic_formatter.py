from app.job_search_agent.schemas.job_knowledge import JobKnowledge

def format_job_semantic_document(
    structured_jobs: list[JobKnowledge]
) -> list[str]:
    """
    Converts structured JobKnowledge objects into semantic
    documents suitable for embedding.
    """

    semantic_documents = []

    for job in structured_jobs:

        semantic_text = f"""
Job Title:
{job.job_title}

Company:
{job.company_name}

Location:
{job.location}

Employment Type:
{job.employment_type}

Employment Level:
{job.employment_level}

Work Mode:
{job.work_mode}

Primary Domain:
{job.primary_domain}

Secondary Domains:
{", ".join(job.secondary_domains)}

Required Technologies:
{", ".join(job.required_technologies)}

Preferred Technologies:
{", ".join(job.preferred_technologies)}

Required Capabilities:
{", ".join(job.required_capabilities)}

Preferred Capabilities:
{", ".join(job.preferred_capabilities)}

Required Degrees:
{", ".join(job.required_degrees)}

Preferred Degrees:
{", ".join(job.preferred_degrees)}

Required Specializations:
{", ".join(job.required_specializations)}

Preferred Specializations:
{", ".join(job.preferred_specializations)}

Required Certifications:
{", ".join(job.required_certifications)}

Preferred Certifications:
{", ".join(job.preferred_certifications)}

Minimum Experience:
{job.minimum_experience_years}

Preferred Experience:
{job.preferred_experience_years}

Responsibilities:
{", ".join(job.responsibilities)}

Benefits:
{", ".join(job.benefits)}

Salary:
{job.salary_information}

Industry:
{job.industry}
"""

        semantic_documents.append(semantic_text.strip())

    return semantic_documents
