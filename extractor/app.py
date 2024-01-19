from utils import YoutubeAudioExtractor
from kafka import KafkaConsumer
import json
import logging
import time

KAFKA_SERVER = ["kafka:19092"]
TOPIC_NAME = "TEST-KAFKA"
GROUP_ID = "youtube-extractor"
CLIENT_ID = "get-links-info"


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
            # reconnect_backoff_max_ms=30000, 재연결 시도
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


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("consumer.conn")

"""카프카 연결 반복 시도
- 카프카 ready 상태에 돌입할 때 까지 연결 재시도
"""
while True:
    try:
        kafkaConsumer = Consumer(KAFKA_SERVER, TOPIC_NAME, CLIENT_ID, GROUP_ID)
        break
    except Exception as e:
        logger.error(f"exception occurred: {e}")
        logger.info("retrying on errors")
        time.sleep(1)
        continue
kafkaConsumer.receive_message()
