# ============================================
# GEMINI TOKEN COST CONFIG
# ============================================

# Gemini 2.5 Flash Lite Pricing
# Approximate pricing per 1K tokens

INPUT_PRICE_PER_1K = 0.000075

OUTPUT_PRICE_PER_1K = 0.00030


# ============================================
# CALCULATE LLM COST
# ============================================

def calculate_llm_cost(

    prompt_tokens: int,

    completion_tokens: int

):

    prompt_cost = (

        prompt_tokens / 1000

    ) * INPUT_PRICE_PER_1K

    completion_cost = (

        completion_tokens / 1000

    ) * OUTPUT_PRICE_PER_1K

    total_cost = (

        prompt_cost +

        completion_cost
    )

    return round(
        total_cost,
        6
    )