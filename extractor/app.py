from utils import YoutubeAudioExtractor
from flask import Flask, request, abort
import os
from pymongo import MongoClient

KAFKA_SERVER = ["kafka-1:19092"]
TOPIC_NAME = "LINKS-YOUTUBE"
GROUP_ID = "get-links-1"
CLIENT_ID = "extractor-links-1"


# config (docker-compose environmnet)
class Config:
    def __init__(self):
        self.MONGO_ID = os.environ.get("MONGO_ID")
        self.MONGO_PW = os.environ.get("MONGO_PW")
        self.MONGO_CLUSTER = os.environ.get("MONGO_CLUSTER")


config = Config()  # 환경변수 등록

# mongoDB Atlas connection
client = MongoClient(
    f"mongodb+srv://{config.MONGO_ID}:{config.MONGO_PW}@{config.MONGO_CLUSTER}.udxtbwr.mongodb.net/?retryWrites=true&w=majority",
)
try:
    client.admin.command("ping")
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client["test"]  # database

app = Flask(__name__)


@app.route("/links", methods=["POST"])
def get_links_information():
    req = request.get_json()

    try:
        links = req["links"]  # string[]
        youtube = YoutubeAudioExtractor(links)
        link_information = youtube.extract_url_information()

        # Insert MongoDB Atlas
        db["youtube"].insert_many(link_information)  # 내부적으로 입력 변수를 bson으롤 바꾼다.
        # print(link_information)
        # return link_information  # jsonify없이 잘 전달됨
        return {"res": "ok"}

    except Exception as err:
        print(err)
        abort(500, description=err)


if __name__ == "__main__":
    app.run(host="extractor-server", port=5000, debug=True)
