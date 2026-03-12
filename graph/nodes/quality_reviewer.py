"""
Quality Reviewer Node — Self-Critique Loop
생성된 스펙 문서를 독립적으로 평가합니다. 점수 미달 시 재생성 요청.
"""
from pathlib import Path
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

from graph.state import GraphState
from schemas.spec import QualityEval

_PROMPT_PATH = Path(__file__).parent.parent.parent / "prompts" / "quality_reviewer_system.md"
_SYSTEM_PROMPT = _PROMPT_PATH.read_text(encoding="utf-8")


def _build_llm():
    from dotenv import load_dotenv
    load_dotenv()
    import os
    llm = ChatGoogleGenerativeAI(
        model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
        temperature=0.0,  # 평가는 결정론적으로
    )
    return llm.with_structured_output(QualityEval)


def run_quality_reviewer(state: GraphState) -> dict:
    """
    품질 검토 노드 (Self-Critique).
    생성된 스펙을 5가지 기준으로 평가하고, 미달 시 개선 힌트를 제공합니다.
    """
    llm = _build_llm()
    final_spec = state.get("final_spec", "")

    messages_for_llm = [
        SystemMessage(content=_SYSTEM_PROMPT),
        HumanMessage(content=f"""[검토할 스펙 문서]
{final_spec}

위 스펙 문서를 5가지 기준으로 평가하고, 개선이 필요한 부분을 지적해 주세요."""),
    ]

    result: QualityEval = llm.invoke(messages_for_llm)

    return {
        "quality_score": result.score,
        "_improvement_hints": result.improvement_suggestions,  # 재생성 시 참조용
        "spec_regeneration_count": state.get("spec_regeneration_count", 0) + 1,
    }
