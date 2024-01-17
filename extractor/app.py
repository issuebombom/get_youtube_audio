from utils import YoutubeAudioExtractor
from kafka import KafkaConsumer
import json

TOPIC_NAME = "TEST-KAFKA"
GROUP_ID = "youtube-extractor"
CLIENT_ID = "get-links-info"
KAFKA_SERVER = "kafka:9092"
 
consumer = KafkaConsumer(
    bootstrap_servers=KAFKA_SERVER,
    group_id=GROUP_ID,
    client_id=CLIENT_ID,
    value_deserializer=lambda v: json.loads(v.decode('utf-8'))
)

consumer.subscribe(TOPIC_NAME)

try:
    for message in consumer:
        message = message.value
        links = message['links']
        
        youtube = YoutubeAudioExtractor(links)
        video_information = youtube.extract_url_information()
        print(video_information)

except Exception as e:
    print({ 'error': f'{e}' })

finally:
    if consumer:
        consumer.close()