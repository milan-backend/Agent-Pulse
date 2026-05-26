import tiktoken


def get_encoding(model_name: str):

    try:

        return tiktoken.encoding_for_model(
            model_name
        )

    except Exception:

        return tiktoken.get_encoding(
            "cl100k_base"
        )


def count_tokens(

    text: str,

    model_name: str = "gpt-4o-mini"

) -> int:

    encoding = get_encoding(
        model_name
    )

    return len(
        encoding.encode(text)
    )