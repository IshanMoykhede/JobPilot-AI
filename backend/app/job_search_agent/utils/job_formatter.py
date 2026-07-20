def format_job_batch(batch: list[dict]) -> str:
    """
    Formats a batch of job dictionaries into a single string.
    """
    formatted_jobs = []
    for i, job in enumerate(batch, 1):
        job_text = f"""
        Job #{i}:
        Title: {job.get("title", "")}
        Company: {job.get("company_name", "")}
        Location: {job.get("location", "")}
        Description:
        {job.get("description", "")}
        """
        formatted_jobs.append(job_text.strip())
    return "\n\n---\n\n".join(formatted_jobs)
