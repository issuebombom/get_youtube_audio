from flask import Flask, request
from werkzeug.exceptions import BadRequest
from utils import YoutubeAudioExtractor
 
app = Flask(__name__)

@app.route('/urls', methods=['POST'])
def get_url_information():
    req = request.get_json()
        
    try:        
        urls = req['urls'] # string
        youtube = YoutubeAudioExtractor(urls)
        urls_information = youtube.extract_url_information()

        return urls_information # jsonify없이 잘 전달됨
    
    except Exception as e:
        return { 'error': f'{e}' }
 
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
