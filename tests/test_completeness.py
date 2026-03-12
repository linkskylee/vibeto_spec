"""
완료도 체크 & 엣지 라우팅 단위 테스트
"""
import pytest
from unittest.mock import patch, MagicMock

from graph.nodes.completeness import run_completeness_check
from graph.edges import route_after_completeness_check, route_after_quality_review


# ── 완료도 노드 테스트 ────────────────────────────────────────────

def test_completeness_updates_checklist(base_state):
    """완료도 체크 노드가 체크리스트를 올바르게 업데이트해야 한다"""
    mock_result = MagicMock()
    mock_result.business_rules = True
    mock_result.edge_cases = False
    mock_result.data_flow = True
    mock_result.constraints = False
    mock_result.target_persona = True
    mock_result.score = 0.6
    mock_result.reasoning = "3/5 항목 수집 완료"

    with patch("graph.nodes.completeness._build_llm") as mock_build:
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = mock_result
        mock_build.return_value = mock_llm

        result = run_completeness_check(base_state)

    assert result["checklist"]["business_rules"] is True
    assert result["checklist"]["edge_cases"] is False
    assert result["completeness_score"] == 0.6


# ── 엣지 라우팅 테스트 ────────────────────────────────────────────

def test_route_to_domain_translator_when_score_high(base_state):
    """완료도 점수 ≥ 0.8이면 domain_translator로 라우팅되어야 한다"""
    state = dict(base_state)
    state["completeness_score"] = 0.8
    state["interview_round"] = 2

    assert route_after_completeness_check(state) == "domain_translator"


def test_route_back_to_interviewer_when_score_low(base_state):
    """완료도 점수 < 0.8이고 라운드 < 5이면 interviewer로 루프백되어야 한다"""
    state = dict(base_state)
    state["completeness_score"] = 0.4
    state["interview_round"] = 2

    assert route_after_completeness_check(state) == "interviewer"


def test_route_to_domain_translator_at_max_rounds(base_state):
    """최대 라운드(5) 도달 시 점수에 관계없이 domain_translator로 진행해야 한다"""
    state = dict(base_state)
    state["completeness_score"] = 0.2  # 낮은 점수
    state["interview_round"] = 5

    assert route_after_completeness_check(state) == "domain_translator"


def test_route_to_end_when_quality_high(base_state):
    """품질 점수 ≥ 0.75이면 END로 라우팅되어야 한다"""
    state = dict(base_state)
    state["quality_score"] = 0.8
    state["spec_regeneration_count"] = 1

    assert route_after_quality_review(state) == "__end__"


def test_route_to_spec_generator_for_regen(base_state):
    """품질 점수 < 0.75이고 재생성 횟수 < 2이면 spec_generator로 라우팅되어야 한다"""
    state = dict(base_state)
    state["quality_score"] = 0.5
    state["spec_regeneration_count"] = 1

    assert route_after_quality_review(state) == "spec_generator"


def test_route_to_end_at_max_regenerations(base_state):
    """최대 재생성 횟수(2) 도달 시 품질 점수에 관계없이 END로 진행해야 한다"""
    state = dict(base_state)
    state["quality_score"] = 0.4  # 낮은 점수
    state["spec_regeneration_count"] = 2

    assert route_after_quality_review(state) == "__end__"
