"""
Completeness Check Node — Phase 1→2 전환 판단
지금까지의 대화를 분석해 요구사항 수집 완료 여부를 평가합니다.
"""
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

from graph.state import GraphState, RequirementsChecklist
from schemas.interview import CompletenessEval

_SYSTEM_PROMPT = """당신은 소프트웨어 요구사항 분석 전문가입니다.
주어진 대화 내용을 분석해, 각 항목이 충분히 파악됐는지 엄격하게 평가합니다.

평가 기준:
- business_rules: 핵심 기능과 규칙이 구체적으로 언급됐는가?
- edge_cases: 실패 케이스나 예외 상황이 최소 1개 이상 언급됐는가?
- data_flow: 입력/출력 또는 데이터 구조가 언급됐는가?
- constraints: 기술 스택, 기한, 규모 등의 제약이 언급됐는가?
- target_persona: 사용자 또는 고객이 구체적으로 정의됐는가?

모호하거나 불충분한 답변은 False로 평가합니다.
score = (True 항목 수) / 5.0 으로 계산합니다."""


def _build_llm():
    from dotenv import load_dotenv
    load_dotenv()
    import os
    llm = ChatGoogleGenerativeAI(
        model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
        temperature=0.0,  # 평가 노드는 결정론적으로
    )
    return llm.with_structured_output(CompletenessEval)


def run_completeness_check(state: GraphState) -> dict:
    """
    완료도 평가 노드.
    대화 전체를 분석해 체크리스트를 업데이트하고 완료 점수를 반환합니다.
    """
    llm = _build_llm()

    # 전체 대화를 텍스트로 변환
    conversation_text = "\n".join([
        f"{msg.type.upper()}: {msg.content}"
        for msg in state.get("messages", [])
    ])

    messages_for_llm = [
        SystemMessage(content=_SYSTEM_PROMPT),
        HumanMessage(content=f"[대화 내용]\n{conversation_text}\n\n위 대화를 분석해 각 항목의 수집 여부를 평가해 주세요."),
    ]

    result: CompletenessEval = llm.invoke(messages_for_llm)

    updated_checklist: RequirementsChecklist = {
        "business_rules": result.business_rules,
        "edge_cases": result.edge_cases,
        "data_flow": result.data_flow,
        "constraints": result.constraints,
        "target_persona": result.target_persona,
    }

    return {
        "checklist": updated_checklist,
        "completeness_score": result.score,
    }
