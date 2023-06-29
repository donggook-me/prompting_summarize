from flask import Flask, jsonify, request
import crawler
import download
import prompt
import json
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config['JSON_AS_ASCII']=False

@app.route('/upload', methods=['POST'])
def urljson():
    url = request.get_json()
    # download.download_func(url['url'])
    # crawler.crawler()
    prompt_instance = prompt.prompt_work("output_1.txt")
    response = prompt_instance.get_resp_text()
    
    print("response is going")
    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(host='0.0.0.0')
