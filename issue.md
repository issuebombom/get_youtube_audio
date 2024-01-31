### New ISSUE (24.01.31)

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