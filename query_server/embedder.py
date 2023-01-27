import openai
from typing import Union
import os
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)

@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def embed_with_backoff(**kwargs):
    return openai.Embedding.create(**kwargs)


DEFAULT_EMBEDDING_MODEL = "text-embedding-ada-002"

class Embedder:

    def __init__(self, model=DEFAULT_EMBEDDING_MODEL):
        self.model = model
        # TODO: switch to dotenv
        openai.api_key = os.environ["OPENAI_API_KEY"]

    # Batch embedding
    def get_embedding(self, text: Union[str, list[str]]) -> Union[list[list[float]], None]:
        try:
            result = embed_with_backoff(model=self.model, input=text)
            return [x["embedding"] for x in result["data"]]
        except Exception as e:
            print(f"ERROR EMBEDDING {e}")
            # TODO: handle exception approriately
            return None
