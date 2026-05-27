from app.utils.tokenizer import (
    count_tokens
)

from app.services.cost_service import (
    calculate_llm_cost
)


# ============================================
# CALCULATE USAGE
# ============================================

def calculate_usage(

    prompt: str,

    completion: str,

    model_name: str

):

    prompt_tokens = count_tokens(

        prompt,

        model_name
    )

    completion_tokens = count_tokens(

        completion,

        model_name
    )

    total_tokens = (

        prompt_tokens +

        completion_tokens
    )

    cost = calculate_llm_cost(

        prompt_tokens=prompt_tokens,

        completion_tokens=completion_tokens
    )

    return {

        "prompt_tokens":
            prompt_tokens,

        "completion_tokens":
            completion_tokens,

        "total_tokens":
            total_tokens,

        "cost":
            float(cost)
    }