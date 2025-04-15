# SKN10-3rd-2Team

# 0. 팀 소개
  ### 팀명: 2팀
<br>

### 팀원 소개

<table align="center" width="100%">
  <tr>
    <td align="center">
      <a href="https://github.com/youngseo98"><b>@편성민</b></a>
    </td>
    <td align="center">
      <a href="https://github.com/Leegwangwoon"><b>@이태수</b></a>
    </td>
    <td align="center">
      <a href="https://github.com/daainn"><b>@권석현</b></a>
    </td>
    <td align="center">
      <a href="https://github.com/ohback"><b>@배민경</b></a>
    </td>
    <td align="center">
      <a href="https://github.com/SIQRIT"><b>@정소열</b></a>
    </td>
  </tr>
</table>

<br>

# 1. 프로젝트 개요

### 프로젝트 명
- BootCampGPT : LLM 기반 부트캠프 학습 Q&A 시스템

### 프로젝트 목표 및 주요 역할
- **목표**: 부트캠프 수강생들이 학습 중 겪는 고충과 질문을 해결하고, 수료생의 회고 데이터를 기반으로 실전적인 인사이트를 제공하는 LLM 기반 Q&A 시스템을 구축하는 것
- **주요 역할**: 학습 중 막힘에 대한 실시간 해결, 실전 기반 피드백 제공, 반복 질문 자동화 대응, 학습 단계별 방향 제시

### 대상
- AI/프로그래밍 부트캠프 수강생, 비전공자, 초심자

### 프로젝트 배경
<div align="center">
  <img src="https://github.com/user-attachments/assets/bbf43abe-b55c-4bdf-aaa2-96f37949285b" width="45%" />
  <img src="https://github.com/user-attachments/assets/b31572cd-0cba-4a12-a521-09b5a1264262" width="45%" />
</div>


- 최근 개발자에 대한 수요가 증가하면서 비전공자들의 개발 학습 참여가 활발해지고 있으나, 여전히 진입 장벽은 높은 상황

- 낯선 용어와 개념, 반복되는 오류와 시행착오 속에서 비전공자들이 학습 과정에서 좌절을 겪는 경우가 많고, 실제로 30명 중 29명이 중도 포기할 만큼 이탈률이 높은 것으로 나타남

- 독학 환경의 한계, 실시간 피드백 부재, 학습 방향에 대한 혼란 등이 주요 원인으로 지적됨

- 이에 따라 학습자가 보다 쉽게 진입하고, 완주할 수 있도록 돕는 지원 환경 조성과 정보 제공의 필요성이 커지고 있음



🔗 **출처**
- https://www.bizhankook.com/bk/article/22027
- https://h21.hani.co.kr/arti/society/society_general/53606.html
  

### 기대효과
- **부트캠프 학습자의 이탈률 감소**: 유사한 상황에서의 실제 경험을 신속하게 참고할 수 있는 구조를 제공함으로써, 비전공자들이 겪는 초기 좌절과 혼란을 줄이고 학습 지속률을 높일 수 있음

- **실전 중심의 피드백 확보**: 단순한 교과서적 설명이 아닌 실제 수강생의 시행착오와 선택 경험이 담긴 응답을 통해, 보다 현실적이고 실행 가능한 도움을 제공

- **부트캠프 운영 측면에서의 교육 질 향상**: 수강생들이 자주 겪는 문제나 질문 유형을 분석해 커리큘럼을 보완하거나 강의 포인트를 조정하는 데 활용 가능

- **수료생 간 지식 공유 문화 형성**: 수료 이후에도 후배 수강생들을 위한 경험 공유가 가능해져, 커뮤니티 기반의 학습문화가 자연스럽게 형성됨

  # 2. 기술 스택

    | 구분 | 기술 | 설명 |
    |------|------|------|
    | **언어/환경** | <img src="https://www.python.org/static/community_logos/python-logo.png" width="40"/> Python, `.env` | 전체 백엔드 로직 구현, 환경 설정 |
    | **웹 프레임워크** | <img src="https://streamlit.io/images/brand/streamlit-logo-secondary-colormark-darktext.png" width="40"/> Streamlit | 사용자 인터페이스 구성 |
    | **데이터 수집** | <img src="https://velog.velcdn.com/images/ujeongoh/post/f135b190-6240-4845-85aa-639246f55740/image.png" width="40"/> requests, BeautifulSoup, fake-useragent | 블로그 및 문서 크롤링 |
    | **데이터 처리** | <img src="https://pandas.pydata.org/static/img/pandas_white.svg" width="40"/> pandas, re, tqdm | 텍스트 전처리 및 필터링 |
    | **문서 처리** | RecursiveCharacterTextSplitter, Document, DataLoader | Q&A 문서 생성 및 청크 분할 |
    | **벡터 저장소** | FAISS (via LangChain) | 문서 임베딩 및 유사 문서 검색 |
    | **임베딩 모델** | <img src="https://img.utdstc.com/icon/6f9/ee0/6f9ee044146aecfd841c98f2a270d996b3e33440142456b9b4349c8bc681857c:200" width="40"/> OllamaEmbeddings, nomic-embed-text | 사용자 쿼리 및 문서 임베딩 처리 |
    | **LLM** | <img src="https://devocean.sk.com/thumnail/2024/8/28/1fc89f92254bed94e769b00b52056d5c6fc64ae7794196218c7050a89fd0852a.png" width="40"/> gemma:2b (Ollama), <img src="https://chatgptfrancais.org/wp-content/uploads/2023/10/ChatGPT-3-2.jpg" width="40"/> OpenAI GPT, <img src="https://huggingface.co/front/assets/huggingface_logo-noborder.svg" width="40"/> llama-cpp | 문맥 기반 응답 생성 |
    | **RAG 엔진** | VectorStore + similarity_search | RAG 기반 질의응답 구현 |
    | **다중 질의 / 재순위화** | MultiQueryRetriever, CrossEncoderReranker | 질의 다양화 및 문서 정렬 향상 |
    | **문서 압축 검색** | ContextualCompressionRetriever | 불필요한 정보 제거한 요약 검색 |
    | **통합 프레임워크** | <img src="https://miro.medium.com/v2/resize:fit:940/1*44fD_VXcqw2kDWublQLONw.jpeg" width="40"/> LangChain | 벡터 검색, 문서 처리, Retriever 구성 등 전체 파이프라인 기반 |


    ---

# 3. 시스템 아키텍처

  ![시스템 아키텍처 다이어그램](drawio.png)



## 주요 구성 파일 설명

| 파일명 | 설명 |
|--------|------|
| `chatbot.py`, `1_🤖_챗봇.py` | Streamlit UI에서 질문 받고 응답 생성 |
| `vector_store.py` | 벡터 저장소 구축 및 유사 문서 검색 핵심 모듈 |
| `embedding_model.py` | nomic-embed-text 기반 임베딩 처리 |
| `llm_model.py` | llama-cpp 로드 및 프롬프트 기반 텍스트 생성 |
| `retriever.py` | 다중 쿼리 및 압축 검색 리트리버 생성기 |
| `reranker.py` | CrossEncoder 기반 재순위화기 적용 |
| `data_loader.py` | CSV를 LangChain Document로 로딩 |
| `document_processor.py` | 문서 청크 분할 처리 |

---

## 작동 흐름 요약 (RAG Pipeline)

1. 사용자가 질문을 입력하면 `chatbot.py`가 처리
2. `VectorStore`를 통해 관련 문서 검색
3. 필요 시 다중 쿼리/재순위화 적용 (retriever, reranker)
4. 최종 context를 기반으로 LLM이 응답 생성
5. Streamlit UI로 결과 출력

---

## 향후 개선 방향

- LLM 응답의 출처 명시 기능 추가
- 질의 히스토리 기반 문맥 강화
- 모델 추론 속도 개선을 위한 양자화된 LLM 우선 활용
- 데이터 증강 기반 파인튜닝 검토

---

# 4. 데이터 수집 및 전처리 안내

1). 데이터 출처

- 본 데이터는 주로 네이버 및 유튜브 플랫폼에서 수집

- 네이버 블로그: 네이버 검색 API 및 웹 크롤링

- 유튜브 영상: 유튜브 자막을 API를 통해 직접 수집

2). 데이터 수집 방법

- 네이버 블로그, tistory, google 등

- 네이버 개발자센터에서 발급받은 비로그인 오픈 API 키 (Client ID, Client Secret) 사용

- 크롤링 시 브라우저 환경을 모방하기 위해 다음과 같은 헤더 사용:

![image](https://github.com/user-attachments/assets/c71b40c8-6e21-4901-8e23-7563b3955fc1)

-세션 유지 및 IP 차단 방지를 위한 시간 간격(2~3초)을 두고 수집 진행

- 유튜브 영상 : YouTube Data API 사용

- 영상 ID, URL, 제목, 업로드 날짜, 채널명, 자막 정보 수집

3). 데이터 형식 및 구조

- 수집된 데이터는 CSV 형식으로 저장됨

- 주요 컬럼:

id: 유튜브 영상 고유 ID

url: 영상 URL

upload_date: 영상 업로드 날짜

channel: 유튜브 채널 이름

title: 영상 제목

caption: 영상 자막 내용

4). 데이터 전처리

- 수집된 데이터 중 다음의 비속어나 18금 단어를 포함한 데이터를 필터링 처리:

  필터링 기준: 제목 및 자막에서 위 단어 포함 여부를 판단하여 제외

5). 데이터 용도 및 주의사항

- 본 데이터는 비전공자의 개발자 취업 현황, 국비지원 교육 프로그램 효과성 분석 등 학습 및 연구 목적으로 활용될 수 있습니다.

- 데이터 사용 시 저작권 및 개인 정보 보호를 준수해야 합니다.

- 상업적 목적이나 타인에게 피해를 줄 수 있는 용도로 사용하지 말아야 합니다.



# 5. 요구사항 명세서

## 1. 기능적 요구사항

## 1.1 AI 챗봇 대화
### 기능
- 사용자와 실시간으로 대화하며 부트캠프에 관련된 다양한 질문에 응답

### 요구사항
- 사용자가 입력한 질문에 대해 즉시 반응할 수 있는 빠른 응답 시스템
- 부트캠프 관련 정보 (학습 자료, 진행 상황 등)에 대한 실시간 답변 제공
- 챗봇이 제공하는 정보는 Q&A 형식으로 쉽게 확인 가능하도록 설계
- 첫 사용자는 설정 안내 후 사용이 가능하도록 초기 설정 가이드 제공

## 1.2 종합 정보 제공
### 기능
- 부트캠프에 필요한 종합적인 정보를 제공

### 요구사항
- 중요한 날짜, 일정, 학습 자료 등 다양한 부트캠프 관련 정보 제공
- 부트캠프의 진행 상황 및 중요한 정보를 정리하여 UI에서 쉽게 접근할 수 있도록 구성

## 1.3 실습 코드 및 피드백 제공
### 기능
- 참가자가 실습 코드와 피드백을 확인할 수 있는 기능 제공

### 요구사항
- 수업에 필요한 실습 코드를 입력한 후, 피드백을 바로 받을 수 있는 시스템
- 피드백 받은 날짜와 코드 예시를 함께 제공하여 학습 효과 향상
- 피드백 받은 코드를 통해 학습자가 실습 문제를 해결할 수 있도록 지원

## 1.4 핵심 가이드
### 기능
- 부트캠프 핵심 가이드 제공

### 요구사항
- 참가자가 필요한 핵심 가이드를 쉽게 확인할 수 있도록 인터페이스 제공
- 각 가이드는 부트캠프 관련 문제 해결 및 학습 방법을 안내


