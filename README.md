# 🧠 Vibe-to-Spec 프롬프트 아키텍트

> 막연한 아이디어(Vibe)를 AI 에이전트가 즉시 실행할 수 있는 구조화된 스펙 문서(Spec)로 변환하는 챗봇

## 🚀 빠른 시작

### 1. 환경 설정
```bash
# .env.example을 복사해 .env 생성 후 API 키 입력
cp .env.example .env
```

`.env` 파일을 열어 다음 값을 입력하세요:
```
GOOGLE_API_KEY=your_google_api_key_here   # 필수
LANGSMITH_API_KEY=your_key_here           # 선택 (디버깅용)
```

### 2. 패키지 설치 (`uv` 사용 권장)
```bash
# uv 설치 (없는 경우)
pip install uv

# 가상환경 생성 + 패키지 설치
uv sync
```

### 3. 서버 실행 (터미널 2개 필요)
```bash
# 터미널 1: FastAPI 백엔드 실행
uv run uvicorn api.main:app --reload

# 터미널 2: Streamlit 프론트엔드 실행
uv run streamlit run frontend/app.py
```

브라우저에서 `http://localhost:8501` 접속 🎉

---

## 📁 프로젝트 구조

```
vibeto_chatbot/
├── graph/
│   ├── state.py              # LangGraph 전체 상태 정의 (GraphState)
│   ├── edges.py              # 조건부 라우팅 함수
│   ├── builder.py            # 그래프 조립 & 컴파일
│   └── nodes/
│       ├── interviewer.py    # Phase 1: 역질문 생성
│       ├── completeness.py   # Phase 1→2 전환 판단
│       ├── domain_translator.py  # Phase 2: DDD 도메인 매핑
│       ├── spec_generator.py     # Phase 3: 스펙 문서 생성
│       └── quality_reviewer.py  # Phase 3: 자기 평가 루프
│
├── schemas/                  # Pydantic 구조화 출력 스키마
│   ├── interview.py
│   ├── domain.py
│   └── spec.py
│
├── prompts/                  # 시스템 프롬프트 (마크다운)
│   ├── interviewer_system.md
│   ├── domain_translator_system.md
│   ├── spec_generator_system.md
│   └── quality_reviewer_system.md
│
├── api/
│   ├── main.py               # FastAPI 앱 진입점
│   └── routes/chat.py        # /api/chat/message 엔드포인트
│
├── frontend/app.py           # Streamlit 채팅 UI
└── tests/                    # 노드별 단위 테스트
```

---

## 🧪 테스트 실행

```bash
# 전체 테스트
uv run pytest tests/ -v

# 특정 노드만 테스트
uv run pytest tests/test_interviewer.py -v
uv run pytest tests/test_completeness.py -v
```

---

## 🏗️ 아키텍처 (LangGraph 플로우)

```
START → [Interviewer] → [Completeness Check]
                              ↓ (부족)
                         ← 루프백 (max 5라운드)
                              ↓ (충분, score≥0.8)
                    [Domain Translator]
                              ↓
                     [Spec Generator]
                              ↓
                    [Quality Reviewer]
                              ↓ (미달, score<0.75)
                         ← 재생성 (max 2회)
                              ↓ (통과)
                            END ✅
```

---

## 📊 기술 스택

| 레이어 | 기술 |
|---|---|
| LLM 오케스트레이션 | LangGraph 0.2+ |
| LLM | Google Gemini 2.0 Flash |
| 구조화 출력 | Pydantic v2 |
| 백엔드 API | FastAPI |
| 프론트엔드 | Streamlit |
| 관찰성/디버깅 | LangSmith |
| 테스트 | pytest |

---

## 🔍 디버깅 가이드

### LangSmith 트레이싱 활성화
`.env`에서 `LANGSMITH_TRACING=true` 설정 후 [smith.langchain.com](https://smith.langchain.com)에서 노드별 입출력 확인

### 로컬 스텝 디버깅
```python
from graph.builder import graph
from langchain_core.messages import HumanMessage

config = {"configurable": {"thread_id": "debug-001"}}
for step in graph.stream({"messages": [HumanMessage(content="테스트")]}, config):
    print(step)
```
