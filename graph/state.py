"""
GraphState: LangGraph 전체 상태 정의
모든 노드는 이 TypedDict를 읽고 업데이트를 반환합니다.
"""
from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages


class RequirementsChecklist(TypedDict):
    """인터뷰 단계에서 수집해야 할 정보 체크리스트"""
    project_goal: bool      # 프로젝트의 핵심 목적/동기
    business_rules: bool    # 핵심 비즈니스 룰
    edge_cases: bool        # 예외 처리 케이스
    data_flow: bool         # 데이터 흐름
    constraints: bool       # 기술/비즈니스 제약 사항
    target_persona: bool    # 대상 사용자/페르소나


class GraphState(TypedDict):
    # ── 대화 히스토리 ──────────────────────────────────────────
    # add_messages 리듀서: 새 메시지를 자동으로 누적 (덮어쓰지 않음)
    messages: Annotated[list, add_messages]

    # ── 인터뷰 단계 상태 ───────────────────────────────────────
    checklist: RequirementsChecklist        # 수집된 항목 체크리스트
    completeness_score: float               # 0.0 ~ 1.0 (0.8 이상이면 다음 Phase)
    interview_round: int                    # 무한 루프 방지 카운터 (최대 5)

    # ── 도메인 번역 결과 ───────────────────────────────────────
    domain_map: dict                        # DomainMap Pydantic 모델을 dict로 저장

    # ── 최종 출력 ──────────────────────────────────────────────
    final_spec: str                         # 마크다운 형태의 최종 스펙 문서
    quality_score: float                    # 스펙 품질 점수 (0.0 ~ 1.0)
    spec_regeneration_count: int            # 스펙 재생성 횟수 (최대 2)

    # ── 메타 정보 ─────────────────────────────────────────────
    raw_token_count: int                    # 사용자 원본 입력 토큰 추정치
    spec_token_count: int                   # 최종 스펙 토큰 추정치
