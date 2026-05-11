def calculate_openai_cost(
    prompt_tokens: int,
    completion_tokens: int,
):
    
    INPUT_PRICE_PER_1K = 0.03
    OUTPUT_PRICE_PER_1K = 0.06

    input_cost = (
        prompt_tokens / 1000
    ) * INPUT_PRICE_PER_1K

    output_cost = (
        completion_tokens / 1000
    ) * OUTPUT_PRICE_PER_1K

    total_cost = (
        input_cost + output_cost
    )

    return round(total_cost, 4)