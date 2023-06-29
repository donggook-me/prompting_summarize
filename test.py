import openai
import os
import csv
import tiktoken
from dotenv import load_dotenv

# load .env
load_dotenv()


openai.api_key = os.environ.get('OPENAI_API_KEY')
print(openai.api_key)