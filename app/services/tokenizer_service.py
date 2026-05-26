from app.utils.tokenizer import (
    count_tokens
)


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
        prompt_tokens
        +
        completion_tokens
    )

    return {

        "prompt_tokens":
            prompt_tokens,

        "completion_tokens":
            completion_tokens,

        "total_tokens":
            total_tokens
    }