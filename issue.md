# New ISSUE (24.01.31)

## 도커 env 파일 등록

docker-compose에서 env_file 등록 시 파일의 끝이 .env 와 다른 이름을 사용할 시 아래와 같이 인식하지 못하는 현상이 발생한다.

```zsh
WARN[0000] The "MONGO_PW" variable is not set. Defaulting to a blank string.
```

아래 도큐먼트를 참조했음에도 동작하지 않는 이유는 무엇인가??  
[docker-compose env_file 안내](https://docs.docker.com/compose /compose-file/05-services/#env_file)

우선 아래 이슈를 참고하여 문제를 해결했다.  
[docker-compose issues](https://github.com/docker/compose/issues/9443)

아래와 같이 up 하기 전에 env_file을 직접 지정하여 등록하는 방법으로 해결

```zsh
docker-compose --env-file .development.env up -d
```

---

## HTTP와 카프카를 통한 MongoDB 도큐먼트 생성 비교 (부하테스트)

먼저 구현한 서비스의 로직을 살펴보자

> main(nestjs) 서버는 엔드포인트로 유튜브 링크를 전달받습니다.  
> main에서 extractor(python) 서버로 받은 링크 정보를 또 다시 전달합니다.  
> extractor 서버에서 유튜브 링크 관련 정보(메타데이터)를 추출합니다.  
> 정보를 데이터베이스(MongoDB Atlas) 저장합니다.

위 과정에서 axios를 사용하여 http 통신을 하는 것과 카프카 브로커로 메시지를 전달하는 두 가지 방식을 비교해 보았다. 각 서버는 모두 컨테이너로 실행했다.

### axios로 http 요청 후 도큐먼트 생성

먼저 axios로 구현한 코드를 보자

```typescript
// links.service.ts
import { HttpService } from '@nestjs/axios';
import { Injectable, InternalServerErrorException } from '@nestjs/common';
import { InjectModel } from '@nestjs/mongoose';
import { lastValueFrom } from 'rxjs';
import { Link } from './schemas/links.schema';
import { Model } from 'mongoose';

@Injectable()
export class LinksService {
  constructor(
    private httpService: HttpService,
    @InjectModel(Link.name) private linkModel: Model<Link>
  ) {}

  async createLinksInformation({ sendLinksMessageDto }) {
    try {
      const res = await lastValueFrom(
        this.httpService.post('http://extractor-server:5000/links', sendLinksMessageDto)
      );
      const data = res.data;
      return data;
    } catch (err) {
      throw new InternalServerErrorException(err.response?.data ?? err.message);
    }
  }
}
```

axios를 사용하여 httpService 객체를 생성하여 POST 요청을 보낼 때 rxjs의 lastValueFrom 함수로 감싸면 axios의 응답 결과인 Observable을 Promise로 변경할 수 있기 때문에 async/await를 적용할 수 있다.

```python
# app.py
# db는 mongoDB 데이터베이스를 의미한다.

@app.route("/links", methods=["POST"])
def get_links_information():
    req = request.get_json()

    try:
        links = req["links"]  # string[]
        youtube = YoutubeAudioExtractor(links)
        link_information = youtube.extract_url_information()

        # Insert MongoDB Atlas
        db["youtube"].insert_many(link_information)  # 내부적으로 입력 변수를 bson으롤 바꾼다.
        return {"res": "ok"}

    except Exception as err:
        abort(500, description=err)
```

메인 서버에서 보낸 데이터를 받아 youtube 객체를 통해 영상 정보를 획득하여 Atlas에 저장한 뒤 ok를 응답한다. 여기서 아래 두 가지 사실을 기억하자.

> 1. youtube 인스턴스 생성과 정보 획득 로직에서 병목현상이 발생한다. 이는 pytube라는 라이브러리를 기반으로 작동하는데 이 또한 youtube 사이트와의 통신이 존재할 것이다. 그러므로 내부적으로 req/res 작동이 일어나므로 기다릴 수 밖에 없게 된다.
> 2. pymongo의 insert_many 함수 또한 동기적으로 작동한다는 점이다. 그래서 도큐먼트 생성까지 기다리게 된다.

위 부분을 인지한 상태에서 부하테스트를 진행해 보자.
테스트 도구로는 `Artillery`를 사용하였다.

```yaml
config:
  target: http://127.0.0.1:3000
  phases:
    - duration: 10
      arrivalRate: 50
      name: 'duration: 10, arrivalRate: 50'
  defaults:
    headers:
      Content-Type: application/json
      # Authorization: Bearer
      User-Agent: Artillery
scenarios:
  - flow:
      - post:
          url: /links/send-message-axios
          json:
            links: 'https://www.youtube.com/watch?v=5fR9AHlSDtc'
```

http 요청은 `/links/send-message-axios` 엔드포인트로 접근하며 초당 50회 요청을 10초 간 유지하도록 설정한 뒤 테스트를 실행했다. 참고로 테스트 환경은 내 컴퓨터 사양이 매우 좋지 못하지만 같은 조건에서 A와 B를 비교하는 것이라면 큰 문제는 없을 것이라 생각했다.

> 테스트 결과 요약
>
> (duration:10, arrivalRate: 50)  
> ETIMEOUT: 435  
> 201: 65  
> MongoDB Atlas Insert: 447 (53개 생성 안 함)

내 컴퓨터 성능이 턱없이 낮은데다가 컨테이너에서 실행했기 때문일까? 대부분의 요청이 ETIMEOUT 에러를 발생시켰다. (Artillery에서는 10초가 넘으면 해당 에러를 raise한다.) 게다가 평균 응답 속도가 6초가 나올 정도로 어마무시하게 느리게 나왔고, 여기서 강도를 더 높이면 ECONNRESET가 발생하면서 500에러가 뜨기까지 했다.  
어쨌든 총 500개의 요청에 대해서 500 에러가 뜨지 않았지만 `MongoDB Atlas에서는 총 447개의 도큐먼트만 생성되었고, 53개는 생성되지 않았다.` 이유가 무엇일까?? 아무래도 요청 프로세스가 단 시간에 계속 쌓여가면서 컴퓨터 자원의 한계가 문제를 일으키지 않았나 예상한다. 더 자세한 원인은 따로 공부할 필요가 있겠다.

### kafka 브로커로 메시지 pub/sub하여 도큐먼트 생성

nestjs에서 카프카 producer를 설정하는 코드는 이전 글에서 이미 작성하였으므로 생략하고, python에서의 consumer 설정을 살펴보자

```python
# kafka_consumer.py
# 환경변수, 라이브러리 등 생략

class Consumer:
    def __init__(self, broker, topic, client_id, group_id):
        self.consumer = KafkaConsumer(
            topic,
            bootstrap_servers=broker,
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            client_id=client_id,
            group_id=group_id,
            auto_offset_reset="latest",  # earliest, latest
            reconnect_backoff_max_ms=30000,  # 재연결 시도
        )

    def receive_message(self):
        try:
            for message in self.consumer:
                links = message.value["links"]
                youtube = YoutubeAudioExtractor(links)
                link_information = youtube.extract_url_information()

                print(link_information, flush=True)  # flush 적용 시 버퍼에 저장된 내용 출력
                db["youtube"].insert_many(link_information)  # 내부적으로 입력 변수를 bson으롤 바꾼다.
        except Exception as e:
            print(f"Extract Process Error: {e}")
```

Consumer 클래스를 통해 인스턴스를 생성한 뒤 receive_message 함수를 실행하면 consumer가 지정한 브로커와 토픽에 대해 커넥션을 유지한다.

카프카 테스트에서는 nestjs의 엔드포인트로 `/links/send-message-kafka`를 열어주고, 이를 통해 유튜브 링크를 전달하면 producer가 파티션에 담는다.

> 테스트 결과 요약
>
> (duration:10, arrivalRate: 50)  
> 201: 500  
> MongoDB Atlas Insert: 500 (약 10분에 걸쳐 모두 생성됨)

어찌보면 예상했던 결과이지만 평균 응답 속도도 약 213ms로 axios와 비교했을 때 빨랐다. 그도 그럴 것이 `/links/send-message-kafka`로 POST 요청한 응답은 메시지를 파티션에 전달하는 것의 성공 유무와 상관 없이 {res: 'ok'}를 응답하도록 설정했기 때문이다.

하지만 `문제는 도큐먼트를 생성하는데 상당히 오랜 시간이 걸렸다는 점`이다. 왜그럴까 생각했을떄 python에 비동기 처리에 대한 설정을 안했기 때문인 것 같다. 위 코드를 다시 살펴보면 consumer가 for문을 써서 메시지를 하나씩 꺼낸 후 관련 정보를 조회한 뒤 Atlas에 Insert하는 과정을 동기적으로 처리하기 때문이다.

그러므로 매우 느리지만 axios처럼 도큐먼트가 생성되지 않는 현상은 발생하지 않았으므로 `확실히 데이터가 저장될 필요가 있는 작업에서 카프카가 더욱 안정적이다는 생각이 든다.`

> 도큐먼트 생성이 느린 문제를 해결하려면?
>
> asyncio 라이브러리로 도큐먼트 생성을 비동기로 처리한다면 좀 더 속도가 빨라질 것으로 예상한다.  
> 여러 파티션과 그만큼 컨슈머를 생성하여 병렬처리 한다면 속도 개선이 이루어질 것으로 보인다.
