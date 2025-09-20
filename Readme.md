1. Docker Container 실행
`docker pull python:3.12-slim`

`docker run -it -d -v .:/home:rw python:3.12-slim`

`docker exec -it <container number>`

2. library 설치
`apt-get update`

`apt-get install python3`

`apt-get install pip`

`pip install langchain langchain-openai python-dotenv`

3. 관련파일 경로:
docker 내부의 home directory로 volume binding 되어 있음.