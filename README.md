# Youtube Audio Extractor

## 참조

https://gofnrk.tistory.com/137 -> 주키퍼 카프카 도커 컴포즈
https://medium.com/@hussainghazali/building-scalable-microservices-with-nestjs-kafka-postgresql-and-docker-349d89392ce2 -> 카프카js 활용
유튜브 링크를 입력하면 해당 영상의 mp3 파일을 각각 추출 및 편집을 지원합니다.

## 카프카 연결 이슈 해결 과정

- 연결 이슈

  - 연결이 안됨

    - 원인: INTERNAL과 EXTERNAL을 구분해서 연결해야함
    - 가령 INTERNAL은 도커끼리의 통신을 뜻하며, kafka:19092와 같이 연결해야함 그 외 밖에서 연결은 localhost:9092로 설정하면 접속이 가능하다. 물론 이건 나중에 도메인이나 전용 IP로 변경해야 하겠지만

  - 해결 과정
    - 'wurstmeister'라는 이름의 주키퍼, 도커 이미지는 nestjs의 producer로 메시지 저장까지 하는 것 성공함. 그러나 latest consuming이 안된다.
    - 'confluentinc' 카프카 이미지를 변경해서 테스트 중
    - 이거는 카프카 컨테이너 내부 터미널이 없다...consumer테스트를 어찌하나
      -> 'docker-compose exec kafka kafka-console-consumer --topic TEST-KAFKA --from-beginning --bootstrap-server kafka:9092'
  - 파이썬 consumer 코드가 메시지 출력하지 않음
    -> 파이썬 print 함수에 flush=True로 설정하니 출력되었다. flush=True로 설정된 print함수가 실행되기 전까지는 일반 print 내용은 버퍼에 쌓이는 구조인 듯 보였다. 그래서 flush=True 설정된 print를 만나면 한꺼번에 쏟아내는 것으로 보인다.

- 파이썬 consumer와 카프카 연결 이슈

  - 원인: docker-compose로 주키퍼, 카프카, node.js, 파이썬 컨테이너를 한꺼번에 실행하다 보니 카프카가 ready상태가 되기 전에 파이썬 컨슈머가 브로커 연결을 시도한다. 총 두번 연결을 시도하다가 실패하니 NoBrokerAvailable이라는 에러를 내며 서버가 죽는다.
  - 해결 과정: kafka-python 모듈의 KafkaConsumer 옵션 파라미터를 살펴봤다. 그 중 'retry_backoff_ms'옵션이 연관 있어보여 적용했으나 반영되지 않았다.
  - 결론: while True 문과 time.sleep(1)을 통한 재시도 텀을 활용하여 카프카가 레디 상태가 되어 연결이 성공할 때 까지 KafkaConsumer 객체 생성을 반복시켰다. 에러가 발생하면 서버가 죽으니 내부에 try, except를 적용하여 while문이 계속 continue 되도록 하는 방식으로 해결했다.

- 도커 컨테이너 빌드 효율화

  - 원인: 매 빌드 시 npm install과 pip install 과정에서 많은 시간이 소요되었다.
  - 해결: 도커파일의 라이브러리 설치 명령을 앞단에 두어 다시 빌드할 때는 라이브러리에 변동이 없다면 캐시가 적용되어 빌드 시간을 단축시킬 수 있었다. nodejs는 모듈 설치를 분리(npm 설치를 앞단에 두는 방식보다 용량이 50mb 가량줄었음) 했고 파이썬은 pip 설치를 앞단에 두는 방식으로 해결했다.

- 도커가 발생시키는 데이터의 지속적 증가로 서버가 띄워지지 않는 현상 발생
  - 원인: 도커 데스크탑을 쓰는 중인데 캐시가 문제가 되는 듯 했다. (참조: https://docs.docker.com/desktop/faqs/macfaqs/)
  - 해결: docker system prune 명령을 적용 (This command removes all stopped containers, unused networks, dangling images, and build cache.)
