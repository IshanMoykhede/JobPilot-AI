from app.job_search_agent.utils.token_counter import count_tokens

def create_token_batches(
    jobs: list[dict],
    system_prompt: str,
    max_context_tokens: int = 10000,
    reserved_output_tokens: int = 2000,
    safety_margin: int = 500,
) -> list[list[dict]]:
    """
    Creates batches of jobs such that the total input tokens
    never exceed the allowed token budget.
    """

    # ---------------------------------------------------------
    # Calculate available token budget for job descriptions
    # ---------------------------------------------------------

    prompt_tokens = count_tokens(system_prompt)

    available_tokens = (
        max_context_tokens
        - prompt_tokens
        - reserved_output_tokens
        - safety_margin
    )

    if available_tokens <= 0:
        raise ValueError(
            "System prompt is too large for the selected model."
        )

    batches = []

    current_batch = []
    current_batch_tokens = 0

    # ---------------------------------------------------------
    # Greedy batching
    # ---------------------------------------------------------

    for job in jobs:
        
        job_text = f"""
        Title: {job.get("title", "")}

        Company: {job.get("company_name", "")}

        Location: {job.get("location", "")}

        Description:
        {job.get("description", "")}
        """

        job_tokens = count_tokens(job_text)

        # If adding this job exceeds our budget,
        # close the current batch.
        if current_batch_tokens + job_tokens > available_tokens:
            if current_batch:
                batches.append(current_batch)

            current_batch = []
            current_batch_tokens = 0

        current_batch.append(job)
        current_batch_tokens += job_tokens

    # Don't forget the last batch
    if current_batch:
        batches.append(current_batch)

    return batches
