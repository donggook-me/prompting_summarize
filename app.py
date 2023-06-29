from flask import Flask, jsonify, request
from flask_cors import CORS
import crawler
import download
import prompt
import json
import os
from dotenv import load_dotenv
load_dotenv()
import openai

app = Flask(__name__)
CORS(app)
app.config['JSON_AS_ASCII'] = False
openai.api_key = os.environ.get('OPENAI_API_KEY')

@app.route('/upload', methods=['POST'])
def urljson():
    url = request.get_json()
    download.download_func(url['url'])
    crawler.crawler()
    prompt_instance = prompt.prompt_work("result.txt")
    response = prompt_instance.get_resp_text()
    
    print("response is going")
    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
