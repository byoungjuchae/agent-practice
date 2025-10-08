# 🤖 AI Agent Practice

LangChain을 활용한 AI 에이전트 실습 프로젝트입니다.

---

## 🐳 1. Docker Container 설정

### Docker 이미지 다운로드
```bash
docker pull python:3.12-slim
```

### 컨테이너 실행
```bash
docker run -it -d -v .:/home:rw python:3.12-slim
```

### 컨테이너 접속
```bash
docker exec -it <container number> /bin/bash
```

---

## 📦 2. Library 설치

### 시스템 업데이트
```bash
apt-get update
```

### Python 및 패키지 관리자 설치
```bash
apt-get install python3
apt-get install pip
```

### LangChain 라이브러리 설치
```bash
pip install langchain langchain-openai python-dotenv
```

---

## ⚠️ 3. 유의사항

- Docker 컨테이너의 `/home` 디렉토리가 현재 작업 디렉토리와 volume binding 되어 있습니다.
- 로컬에서 작성한 파일이 컨테이너 내부의 `/home` 디렉토리에 자동으로 동기화됩니다.



---

## 🚀 시작하기

1. Docker 컨테이너를 실행합니다.
2. 필요한 라이브러리를 설치합니다.
3. `.env` 파일에 필요한 환경 변수를 설정합니다.
4. `hyerim/` 디렉토리의 예제 파일을 실행해보세요!

---

## 💡 도움말

각 예제 파일은 LangChain의 다양한 기능을 학습하기 위한 실습 코드를 포함하고 있습니다.
