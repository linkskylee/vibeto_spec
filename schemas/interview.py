"""
인터뷰 단계 관련 Pydantic 스키마
LLM의 응답을 구조화된 객체로 강제합니다.
"""
from pydantic import BaseModel, Field


class InterviewQuestion(BaseModel):
    """인터뷰어 노드의 출력 스키마"""
    question: str = Field(description="사용자에게 던질 역질문 (한 번에 하나만)")
    target_field: str = Field(
        description="이 질문이 채우려는 체크리스트 항목",
        examples=["business_rules", "edge_cases", "data_flow", "constraints", "target_persona"]
    )
    reasoning: str = Field(description="이 질문을 선택한 이유 (내부 추론, 사용자에게 미노출)")


class CompletenessEval(BaseModel):
    """완료도 평가 노드의 출력 스키마"""
    business_rules: bool = Field(description="핵심 비즈니스 룰 수집 완료 여부")
    edge_cases: bool = Field(description="예외 처리 케이스 파악 여부")
    data_flow: bool = Field(description="데이터 흐름 파악 여부")
    constraints: bool = Field(description="기술/비즈니스 제약 사항 파악 여부")
    target_persona: bool = Field(description="대상 사용자 파악 여부")
    score: float = Field(ge=0.0, le=1.0, description="전체 완료도 점수 (0.0 ~ 1.0)")
    reasoning: str = Field(description="점수 산정 근거")
