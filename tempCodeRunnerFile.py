# load .env
load_dotenv()

class prompt_work():
    openai.api_key = os.environ.get('OPENAI_API_KEY_SERVICE')
    openai.api_key_path = '.env'