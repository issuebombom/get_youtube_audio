# get youtube audio

## MicroService와 Kafka 공부를 위한 서비스 구현

> Goal:
>
> - 유튜브 링크를 클라이언트에서 보내면 해당 유튜브 음원 뿐 아니라 정보, 영상을 추출하는 기능 구현
> - Kafka 기본 구현 및 서비스 적용

> Abstract:
>
> - main-server(nestjs)에서 엔드포인트로 유튜브 링크를 전달받습니다.
> - extractor(python) 서버로 링크 정보를 전달합니다.
> - extractor 서버에서 링크 관련 정보를 추출합니다.
> - 데이터베이스 저장 또는 main-server에 결과를 전달합니다.

> Progress:
>
> - 방법1: nestjs에서 axios를 활용하여 python flask 서버에 링크를 전달하는 방식 구현(http)
> - 방법2: 두 서버 간 브로커를 배치(kafka)
> - 방법2의 경우 도커 컨테이너로 서버 띄우기 (zookeeper, kafka, main-server, extractor-server)

> Result:
>
> - axios와 kafka 두 가지 방법 모두 구현
> - kafka 방식은 docker-compose up으로 실행 (producer: nestjs, consumer: python)
> - 현재 유튜브 링크 전달 시 해당 영상 정보만 출력하는 기능 구현

> Future Plan:
>
> - 유튜브 정보 데이터베이스 저장 구현
> - axios와 broker 속도 비교 테스트
> - 유튜브 음원 및 영상 추출 기능 적용

## Issue

### 카프카와 서버 간 네트워크 연결 이슈

> 문제 및 해결:  
> `컨테이너 간 네트워크 연결이 안됨`
>
> - producer와 consumer 서버에서는 localhost:9092로 브로커 연결을 시도했으나 연결 가능한 브로커가 없다는 에러 메시지 발행됨
> - docker-compose.yaml 작성 시 카프카의 server.properties에서 INTERNAL과 EXTERNAL 연결을 위한 경로를 구분해서 설정해야 함
> - 컨테이너는 내부 IP가 제공되며 동일 환경에서 생성된 컨테이너 간 통신을 위해서는 yaml에 작성한 services의 이름을 반영해야 한다. (ex. kafka:19092)
> - 만약 로컬 환경의 producer, consumer가 카프카 컨테이너에 연결하기 위해서는 localhost:9092로 브로커를 설정해야 한다. 이는 컨테이너 입장에서 외부 접근에 해당하기 때문이다.
> - 당연한 이야기지만 EC2에서 컨테이너를 실행한다면 EXTERNAL 설정을 해당 EC2 IP로 지정해야 한다.

```bash
# docker-compose.yaml
# ...
environment:
  KAFKA_LISTENERS: LISTENER_DOCKER_INTERNAL://:19092,LISTENER_DOCKER_EXTERNAL://:9092
  KAFKA_ADVERTISED_LISTENERS: LISTENER_DOCKER_INTERNAL://kafka:19092,LISTENER_DOCKER_EXTERNAL://localhost:9092
  KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: LISTENER_DOCKER_INTERNAL:PLAINTEXT,LISTENER_DOCKER_EXTERNAL:PLAINTEXT
  KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
  KAFKA_INTER_BROKER_LISTENER_NAME: LISTENER_DOCKER_INTERNAL
depends_on:
  - zookeeper
```

### 파이썬 컨테이너 print 출력 이슈

> 문제 및 해결:  
> `컨테이너 터미널에서 print문이 출력되지 않음.`
>
> - 처음에는 브로커의 파티션에 등록된 메시지가 쌓여 있음에도 파이썬으로 구현한 컨슈머가 구독하지 못하는 것으로 판단함. 이는 메시지 결과를 print문으로 출력하도록 코드 작성 후 테스트를 진행했기 때문임
> - 파티션에 메시지가 적재되지 않는 것을 의심하여 kafka-console-consumer.sh를 활용하여 테스트해 본 결과 메시지가 잘 적재되고 컨슈머가 잘 받아오는 것을 확인함
> - 로컬 환경에서 컨슈머를 실행하여 테스트해 본 결과 카프카 컨테이너에서 받아온 메시지가 print문으로 잘 확인되었고, 이 시점에서 파이썬 컨테이너의 print 출력에 대한 의심을 하게 됨
> - 파이썬 컨테이너에서는 print 옵션으로 `flush=True`로 설정한 print가 등장하기 전까지는 버퍼에 내용을 쌓아둔다는 점을 파악함
> - 결론적으로 컨슈머 컨테이너는 카프카 컨테이너와 잘 연결된 상태였었고, 단지 메시지 출력을 print로 확인하려 했기 때문에 노출이 되지 않았을 뿐임을 확인

### 컨슈머와 카프카의 연결 이슈

> 문제 및 해결:  
> `파이썬 컨슈머는 브로커가 READY 상태가 될 때까지 연결 재시도를 하지 않고 연결 오류 발생 후 서버 다운됨`
>
> - docker-compose up으로 카프카와 컨슈머를 실행하는데 컨슈머가 카프카의 준비완료를 기다리지 않음
> - docker-compose의 depends_on: kafka를 컨슈머 서버에 적용했으나, 이는 카프카 컨테이너의 실행까지만 기다려 줄 뿐 ready상태에 돌입할 때 까지 기다려주지는 않으므로 해결되지 않음
> - kafka-python 패키지를 사용하여 KafkaConsumer 객체를 생성할 때 연결을 지속적으로 재시도하는 옵션을 찾아봄
> - 도큐먼트를 참조하여 `retry_backoff_ms` 옵션이 원하는 기능으로 판단되어 30초로 설정해 보았으나 해결되지 않음
> - while문으로 직접 만들기로 하여 아래와 같이 코드를 작성하여 문제를 해결함

```python
# app.py
"""
- Consumer는 직접 만든 클래스
- while문 내 try, except를 활용하여 객체 생성에 실패하면 logger를 띄우고 객체 재생성을 시도함
"""
while True:
    try:
        kafkaConsumer = Consumer(KAFKA_SERVER, TOPIC_NAME, CLIENT_ID, GROUP_ID)
        break
    except Exception as e:
        logger.error(f"exception occurred: {e}")
        logger.info("retrying on errors")
        time.sleep(1) # wait 1 sec.
        continue
kafkaConsumer.receive_message()
```

### 도커 컨테이너 생성의 효율성

> 문제 및 해결:  
> `코드 수정 후 컨테이너 실행 시 속도 문제 및 이미지 크기 문제`
>
> - nodejs:18, python:3.8 Dockerfile 작성 시 라이브러리 설치를 앞단에 배치하여 코드 수정 후 다시 빌드할 때 npm, pip install 부분은 캐시를 참조하여 최초 빌드 후 속도 단축됨
> - alpine 이미지를 적용하여 이미지 용량 축소
> - 주키퍼와 카프카 이미지는 대표적으로 'wurstmeister'와 'confluentinc'가 알려져 있었으나 둘 다 기본 사용에 큰 문제는 없었고, 이미지 용량이 더 작은 wurstmeister를 채택 (하지만 confluentinc는 카프카 전직원으로 구성된 그룹에서 만든 이미지라고 하여 뭔지 모를 신뢰도가 있긴 함)

#### nodejs Dockerfile 살펴보기

```dockerfile
# 방법 1
FROM node:18 AS builder
WORKDIR /app
COPY package*.json /app/
RUN npm install

FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/node_modules/ /app/node_modules/
COPY . .
RUN npm run build
CMD ["node", "dist/main.js"]

# ---------------------------------------

# 방법 2
# 해당 방식의 이미지 크기가 50mb 더 차지함
FROM node:18-alpine
WORKDIR /app
COPY package*.json /app/
RUN npm install
COPY . .
RUN npm run build
CMD ["node", "dist/main.js"]
```

`방법 1` 의 경우 라이브러리 설치 과정과 그 결과인 node_modules폴더를 복사하는 과정을 분리하였고, `방법 2` 의 경우 하나의 과정에 모두 담았다.  
재빌드할 경우 단축되는 시간은 체감상 비슷했다. 라이브러리 설치 구간이 캐시를 이용하기 때문일 것이다. 최초 빌드 시간은 방법1이 더 오래걸렸다. 하지만 이미지 용량은 50mb 더 단축할 수 있었다. 이는 npm install 실행에 필요한 리소스를 배제할 수 있었기 때문이 아닐까 예상한다.

#### python Dockerfile 살펴보기

```dockerfile
FROM python:3.8-alpine
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD python app.py
```

### 갑자기 컨테이너 빌드 및 실행이 되지 않는 현상 발생

> 문제 및 해결:  
> `도커 데스크탑 사용으로 인해 적재된 캐시가 지속적으로 용량을 차지하여 디스크 공간 부족을 일으킴`
>
> 설정에서 virtual disk limit의 용량을 줄였다. 도커 데스크탑에서 해당 옵션에 설정된 크기만큼 디스크 공간을 차지하였고, 이를 줄였다.  
> docker system prune 명령어를 실행하여 불필요한 데이터를 제거하였다.  
> [문서 참조: "This command removes all stopped containers, unused networks, dangling images, and build cache."]  
> (참조: https://docs.docker.com/desktop/faqs/macfaqs/)

### Reference

[카프카 Quickstart](https://kafka.apache.org/quickstart)  
[nestjs-kafka](https://docs.nestjs.com/microservices/kafka)  
[kafkajs 설정](https://medium.com/@hussainghazali/building-scalable-microservices-with-nestjs-kafka-postgresql-and-docker-349d89392ce2)  
[kafka-python 패키지](https://kafka-python.readthedocs.io/en/master/index.html)  
[confluent-kafka-python 패키지](https://github.com/confluentinc/confluent-kafka-python)  
[카프카 docker-compose.yaml 작성1](https://github.com/wurstmeister/kafka-docker)  
[카프카 docker-compose.yaml 작성2](https://devocean.sk.com/blog/techBoardDetail.do?ID=164016)
