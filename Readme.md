1. Docker Container ����
`docker pull python:3.12-slim`

`docker run -it -d -v .:/home:rw python:3.12-slim`

`docker exec -it <container number>`

2. library ��ġ
`apt-get update`

`apt-get install python3`

`apt-get install pip`

`pip install langchain langchain-openai python-dotenv`

3. �������� ���:
docker ������ home directory�� volume binding �Ǿ� ����.