import os
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()


def get_llm_client() -> AzureOpenAI:
    return AzureOpenAI(
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        api_version=os.environ["AZURE_OPENAI_API_VERSION"],
    )


def chat_completion(messages: list[dict], temperature: float = 0.3, response_format=None) -> str:
    client = get_llm_client()
    kwargs = {
        "model": os.environ["AZURE_OPENAI_LLM_DEPLOYMENT"],
        "messages": messages,
        "temperature": temperature,
    }
    if response_format:
        kwargs["response_format"] = response_format
    response = client.chat.completions.create(**kwargs)
    return response.choices[0].message.content


def chat_completion_json(messages: list[dict], temperature: float = 0.2) -> str:
    return chat_completion(messages, temperature, response_format={"type": "json_object"})
