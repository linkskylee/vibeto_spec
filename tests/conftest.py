"""
pytest 공통 픽스처 — 모든 테스트에서 재사용
"""
import pytest
from unittest.mock import MagicMock
from langchain_core.messages import HumanMessage, AIMessage

from graph.state import GraphState


@pytest.fixture
def base_state() -> GraphState:
    """기본 초기 상태 픽스처"""
    return {
        "messages": [HumanMessage(content="쇼핑몰 만들고 싶어요")],
        "checklist": {
            "business_rules": False,
            "edge_cases": False,
            "data_flow": False,
            "constraints": False,
            "target_persona": False,
        },
        "completeness_score": 0.0,
        "interview_round": 0,
        "domain_map": {},
        "final_spec": "",
        "quality_score": 0.0,
        "spec_regeneration_count": 0,
        "raw_token_count": 0,
        "spec_token_count": 0,
    }


@pytest.fixture
def completed_interview_state(base_state) -> GraphState:
    """인터뷰가 완료된 상태 픽스처 (Phase 2 테스트용)"""
    state = dict(base_state)
    state["messages"] = [
        HumanMessage(content="쇼핑몰 만들고 싶어요"),
        AIMessage(content="주요 판매 상품 카테고리는 무엇인가요?"),
        HumanMessage(content="의류와 잡화를 팔 예정이에요"),
        AIMessage(content="결제 방법은 어떻게 처리할 예정인가요?"),
        HumanMessage(content="카드와 계좌이체를 지원하고, 결제 실패 시 재시도 기능이 필요해요"),
    ]
    state["checklist"] = {
        "business_rules": True,
        "edge_cases": True,
        "data_flow": True,
        "constraints": False,
        "target_persona": True,
    }
    state["completeness_score"] = 0.8
    state["interview_round"] = 3
    return state
