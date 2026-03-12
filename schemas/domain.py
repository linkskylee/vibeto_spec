"""
도메인 번역 관련 Pydantic 스키마
비즈니스 언어를 DDD 기반 도메인 모델로 매핑합니다.
"""
from pydantic import BaseModel, Field


class Entity(BaseModel):
    """DDD 엔티티 정의"""
    name: str = Field(description="엔티티 이름 (예: User, Order, Product)")
    attributes: list[str] = Field(description="엔티티가 가지는 주요 속성 목록")
    description: str = Field(description="이 엔티티의 역할 설명")


class Action(BaseModel):
    """도메인 액션(유즈케이스) 정의"""
    name: str = Field(description="액션 이름 (동사_명사 형태, 예: create_order)")
    actor: str = Field(description="이 액션을 수행하는 주체 (예: User, Admin)")
    description: str = Field(description="이 액션이 하는 일")
    business_rule: str = Field(description="이 액션에 적용되는 핵심 비즈니스 규칙")


class FolderStructure(BaseModel):
    """권장 폴더 구조"""
    structure: str = Field(description="트리 형태의 폴더 구조 (마크다운 코드블록 내용)")
    rationale: str = Field(description="이 구조를 선택한 이유")


class DomainMap(BaseModel):
    """도메인 번역 노드의 최종 출력 스키마"""
    project_name: str = Field(description="프로젝트 이름 (영문, snake_case)")
    bounded_context: str = Field(description="이 프로젝트의 핵심 도메인 컨텍스트")
    entities: list[Entity] = Field(description="식별된 핵심 엔티티 목록")
    actions: list[Action] = Field(description="식별된 핵심 액션(유즈케이스) 목록")
    folder_structure: FolderStructure = Field(description="AI 에이전트가 따를 권장 폴더 구조")
