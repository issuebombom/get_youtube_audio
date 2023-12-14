from flask import Flask, request
from werkzeug.exceptions import BadRequest
from utils import YoutubeAudioExtractor
 
app = Flask(__name__)

@app.route('/urls')
def get_url_information():
    req = request.get_json()

    # 필수 body key가 없을 경우 예외 처리
    if 'urls' not in req.keys():
        raise BadRequest(f'Missing required field: urls')
        
    urls_str = req['urls'] # string

    youtube = YoutubeAudioExtractor(urls_str)

    urls_information = youtube.extract_url_information()
    
    return urls_information # jsonify없이 잘 전달됨
 
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
