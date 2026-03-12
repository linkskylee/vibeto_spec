"""
Domain Translator Node — Phase 2
수집된 비즈니스 언어를 DDD 기반 도메인 모델로 변환합니다.
"""
from pathlib import Path
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

from graph.state import GraphState
from schemas.domain import DomainMap

_PROMPT_PATH = Path(__file__).parent.parent.parent / "prompts" / "domain_translator_system.md"
_SYSTEM_PROMPT = _PROMPT_PATH.read_text(encoding="utf-8")


def _build_llm():
    from dotenv import load_dotenv
    load_dotenv()
    import os
    llm = ChatGoogleGenerativeAI(
        model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
        temperature=0.2,
    )
    return llm.with_structured_output(DomainMap)


def run_domain_translator(state: GraphState) -> dict:
    """
    도메인 번역 노드.
    인터뷰 결과를 DDD 엔티티/액션/폴더구조로 변환합니다.
    """
    llm = _build_llm()

    # 전체 대화 내용으로 도메인 번역 요청
    conversation_text = "\n".join([
        f"{msg.type.upper()}: {msg.content}"
        for msg in state.get("messages", [])
    ])

    messages_for_llm = [
        SystemMessage(content=_SYSTEM_PROMPT),
        HumanMessage(content=f"""[수집된 인터뷰 내용]
{conversation_text}

위 내용을 바탕으로 도메인 모델을 추출해 주세요.
프로젝트 이름, 핵심 엔티티, 액션, 권장 폴더 구조를 포함해야 합니다."""),
    ]

    result: DomainMap = llm.invoke(messages_for_llm)

    return {
        "domain_map": result.model_dump(),
    }
