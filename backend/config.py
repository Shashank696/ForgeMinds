import sys
import os
from functools import lru_cache
from pydantic_settings import BaseSettings

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class Settings(BaseSettings):
    # TODO: Define all env vars from .env.example
    pass

@lru_cache()
def get_settings():
    return Settings()
