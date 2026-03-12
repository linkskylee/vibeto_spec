"""
Graph Builder — LangGraph 그래프 조립
모든 노드와 엣지를 연결해 실행 가능한 그래프를 반환합니다.
"""
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from graph.state import GraphState
from graph.nodes.interviewer import run_interviewer
from graph.nodes.completeness import run_completeness_check
from graph.nodes.domain_translator import run_domain_translator
from graph.nodes.spec_generator import run_spec_generator
from graph.nodes.quality_reviewer import run_quality_reviewer
from graph.edges import route_after_completeness_check, route_after_quality_review


def build_graph(use_checkpointer: bool = True):
    """
    LangGraph 그래프를 조립하고 컴파일합니다.

    Args:
        use_checkpointer: True이면 MemorySaver 체크포인터 적용 (대화 중단/재개 지원)

    Returns:
        컴파일된 LangGraph 그래프 인스턴스
    """
    builder = StateGraph(GraphState)

    # ── 노드 등록 ────────────────────────────────────────────────
    builder.add_node("interviewer", run_interviewer)
    builder.add_node("completeness_check", run_completeness_check)
    builder.add_node("domain_translator", run_domain_translator)
    builder.add_node("spec_generator", run_spec_generator)
    builder.add_node("quality_reviewer", run_quality_reviewer)

    # ── 엣지 연결 ────────────────────────────────────────────────
    # 진입점: 항상 인터뷰어부터 시작
    builder.set_entry_point("interviewer")

    # interviewer → completeness_check (항상)
    builder.add_edge("interviewer", "completeness_check")

    # completeness_check → (interviewer | domain_translator) 조건부
    builder.add_conditional_edges(
        "completeness_check",
        route_after_completeness_check,
        {
            "interviewer": "interviewer",
            "domain_translator": "domain_translator",
        }
    )

    # domain_translator → spec_generator (항상)
    builder.add_edge("domain_translator", "spec_generator")

    # spec_generator → quality_reviewer (항상)
    builder.add_edge("spec_generator", "quality_reviewer")

    # quality_reviewer → (spec_generator | END) 조건부
    builder.add_conditional_edges(
        "quality_reviewer",
        route_after_quality_review,
        {
            "spec_generator": "spec_generator",
            "__end__": END,
        }
    )

    # ── 컴파일 ──────────────────────────────────────────────────
    if use_checkpointer:
        # MemorySaver: 메모리 기반 체크포인터 (프로덕션은 SqliteSaver 사용)
        checkpointer = MemorySaver()
        return builder.compile(checkpointer=checkpointer)

    return builder.compile()


# 기본 그래프 인스턴스 (앱 전체에서 재사용)
graph = build_graph()
