from utils import YoutubeAudioExtractor
from flask import Flask, request, abort
from kafka import KafkaConsumer
import json
import os
from pymongo import MongoClient
import logging
import time

KAFKA_SERVER = ["kafka-1:19092"]
TOPIC_NAME = "LINKS-YOUTUBE"
GROUP_ID = "get-links-1"
CLIENT_ID = "extractor-links-1"


class Consumer:
    def __init__(self, broker, topic, client_id, group_id):
        self.consumer = KafkaConsumer(
            topic,
            bootstrap_servers=broker,
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            client_id=client_id,
            group_id=group_id,
            auto_offset_reset="latest",  # earliest, latest
            # retry_backoff_ms=30000, # 연결 시도
            reconnect_backoff_max_ms=30000,  # 재연결 시도
            # enable_auto_commit=True, # 오프셋 자동 커밋 여부
            # consumer_timeout_ms=1000 # 데이터 이터레이션을 막는 시간
        )

    def receive_message(self):
        try:
            for message in self.consumer:
                print(message.value)
                links = message.value["links"]
                youtube = YoutubeAudioExtractor(links)
                video_information = youtube.extract_url_information()
                print(video_information, flush=True)  # flush 적용 시 버퍼에 저장된 내용 출력
        except Exception as e:
            print(f"Extract Process Error: {e}")


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
    # logging.basicConfig(level=logging.INFO)
    # logger = logging.getLogger("consumer.conn")

    # """카프카 연결 반복 시도
    # - 카프카 ready 상태에 돌입할 때 까지 연결 재시도
    # """
    # while True:
    #     try:
    #         kafkaConsumer = Consumer(KAFKA_SERVER, TOPIC_NAME, CLIENT_ID, GROUP_ID)
    #         break
    #     except Exception as e:
    #         logger.error(f"exception occurred: {e}")
    #         logger.info("retrying on errors")
    #         time.sleep(1)
    #         continue
    # kafkaConsumer.receive_message()
