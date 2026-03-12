"""
최종 스펙 문서 관련 Pydantic 스키마
Agent-ready 마크다운 스펙의 구조를 정의합니다.
"""
from pydantic import BaseModel, Field


class SpecContext(BaseModel):
    """[1. Context] 섹션: 프로젝트 배경 및 환경"""
    project_name: str
    background: str = Field(description="왜 이 프로젝트를 만드는가")
    target_persona: str = Field(description="누가 이 소프트웨어를 사용하는가")
    tech_stack: list[str] = Field(description="사용할 기술 스택 목록")
    constraints: list[str] = Field(description="기술/비즈니스 제약 사항")


class SpecTask(BaseModel):
    """[2. Task] 섹션: 구현 요청 세부사항"""
    objective: str = Field(description="한 문장으로 요약한 구현 목표")
    domain_entities: list[str] = Field(description="구현에 필요한 핵심 엔티티 목록")
    actions: list[str] = Field(description="구현할 핵심 액션(API/기능) 목록")
    business_rules: list[str] = Field(description="반드시 지켜야 할 비즈니스 규칙")
    edge_cases: list[str] = Field(description="처리해야 할 예외 상황 목록")
    folder_structure: str = Field(description="권장 폴더 구조 (마크다운 코드블록)")


class SpecTest(BaseModel):
    """[3. Test] 섹션: 결과 검증 체크리스트"""
    success_criteria: list[str] = Field(description="구현 성공 판단 기준 목록")
    test_scenarios: list[str] = Field(description="검증해야 할 테스트 시나리오 목록")
    acceptance_conditions: list[str] = Field(description="최종 승인 조건 목록")


class QualityEval(BaseModel):
    """품질 검토 노드의 출력 스키마"""
    score: float = Field(ge=0.0, le=1.0, description="스펙 품질 점수 (0.0 ~ 1.0)")
    is_actionable: bool = Field(description="AI 에이전트가 즉시 실행 가능한가")
    missing_elements: list[str] = Field(description="누락된 요소 목록 (있을 경우)")
    improvement_suggestions: list[str] = Field(description="개선 제안 목록")


class FinalSpec(BaseModel):
    """스펙 생성 노드의 최종 출력 스키마"""
    context: SpecContext
    task: SpecTask
    test: SpecTest
    token_estimate: int = Field(description="이 스펙 문서의 예상 토큰 수")
