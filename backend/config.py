from dotenv import load_dotenv
import os

load_dotenv()

# Get the environment variables
class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    MODEL_NAME = "gpt-5.5"