"""
Interviewer Node — Phase 1
사용자의 초기 아이디어를 받아 부족한 정보를 역으로 질문합니다.
"""
from pathlib import Path
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from graph.state import GraphState
from schemas.interview import InterviewQuestion

# 시스템 프롬프트 파일에서 로드 (코드와 프롬프트 분리)
_PROMPT_PATH = Path(__file__).parent.parent.parent / "prompts" / "interviewer_system.md"
_SYSTEM_PROMPT = _PROMPT_PATH.read_text(encoding="utf-8")


def _build_llm() -> ChatGoogleGenerativeAI:
    """구조화 출력용 LLM 인스턴스 생성"""
    from dotenv import load_dotenv
    load_dotenv()
    import os
    llm = ChatGoogleGenerativeAI(
        model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
        temperature=0.3,
    )
    return llm.with_structured_output(InterviewQuestion)


def run_interviewer(state: GraphState) -> dict:
    """
    인터뷰어 노드 실행 함수.

    Args:
        state: 현재 GraphState

    Returns:
        업데이트할 상태 필드 딕셔너리
    """
    llm = _build_llm()

    # 체크리스트 현황을 프롬프트에 포함
    checklist = state.get("checklist", {
        "business_rules": False,
        "edge_cases": False,
        "data_flow": False,
        "constraints": False,
        "target_persona": False,
    })
    checklist_summary = "\n".join([
        f"- {'✅' if v else '❌'} {k}" for k, v in checklist.items()
    ])

    # 시스템 메시지 + 기존 대화 히스토리 + 체크리스트 현황 전달
    messages_for_llm = [
        SystemMessage(content=_SYSTEM_PROMPT),
        *state.get("messages", []),
        HumanMessage(content=f"[현재 체크리스트 현황]\n{checklist_summary}\n\n위 현황을 참고해 가장 중요한 미수집 정보 하나를 질문해 주세요."),
    ]

    result: InterviewQuestion = llm.invoke(messages_for_llm)

    # 인터뷰어의 질문을 AI 메시지로 추가
    new_message = AIMessage(content=result.question)

    return {
        "messages": [new_message],
        "interview_round": state.get("interview_round", 0) + 1,
    }
