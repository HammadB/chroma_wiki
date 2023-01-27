from pydantic import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str
    wiki_db_path: str
    index_path: str
    wikipedia_local_index_path: str
    wikipedia_local_dump_path: str

    class Config:
        env_file = ".env"

settings = Settings()