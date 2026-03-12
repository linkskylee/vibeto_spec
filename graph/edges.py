"""
조건부 엣지 함수 — 노드 간 라우팅 로직
각 함수는 다음에 실행할 노드 이름을 반환합니다.
"""
from graph.state import GraphState

# 인터뷰 최대 라운드 수 (무한 루프 방지)
MAX_INTERVIEW_ROUNDS = 5
# 완료도 임계값
COMPLETENESS_THRESHOLD = 0.8
# 품질 임계값
QUALITY_THRESHOLD = 0.75
# 스펙 재생성 최대 횟수
MAX_SPEC_REGENERATIONS = 2


def route_after_completeness_check(state: GraphState) -> str:
    """
    완료도 체크 후 라우팅.
    - 점수 ≥ 0.8 이거나 최대 라운드 도달 → domain_translator
    - 그 외 → interviewer (루프백)
    """
    score = state.get("completeness_score", 0.0)
    rounds = state.get("interview_round", 0)

    if score >= COMPLETENESS_THRESHOLD or rounds >= MAX_INTERVIEW_ROUNDS:
        print(f"[Router] 인터뷰 완료 → domain_translator (score={score:.2f}, rounds={rounds})")
        return "domain_translator"

    print(f"[Router] 추가 질문 필요 → interviewer (score={score:.2f}, rounds={rounds})")
    return "interviewer"


def route_after_quality_review(state: GraphState) -> str:
    """
    품질 검토 후 라우팅.
    - 점수 ≥ 0.75 이거나 재생성 횟수 ≥ 2 → END
    - 그 외 → spec_generator (재생성)
    """
    score = state.get("quality_score", 0.0)
    regen_count = state.get("spec_regeneration_count", 0)

    if score >= QUALITY_THRESHOLD or regen_count >= MAX_SPEC_REGENERATIONS:
        print(f"[Router] 스펙 확정 → END (score={score:.2f}, regen={regen_count})")
        return "__end__"

    print(f"[Router] 스펙 재생성 → spec_generator (score={score:.2f}, regen={regen_count})")
    return "spec_generator"
