"""
인터뷰어 노드 단위 테스트
LLM을 mock 처리해 비즈니스 로직만 독립적으로 검증합니다.
"""
import pytest
from unittest.mock import patch, MagicMock
from langchain_core.messages import AIMessage

from graph.nodes.interviewer import run_interviewer


def test_interviewer_increments_round(base_state):
    """매번 호출 시 interview_round가 1씩 증가해야 한다"""
    mock_result = MagicMock()
    mock_result.question = "주요 기능이 무엇인가요?"
    mock_result.target_field = "business_rules"
    mock_result.reasoning = "비즈니스 규칙 미수집"

    with patch("graph.nodes.interviewer._build_llm") as mock_build:
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = mock_result
        mock_build.return_value = mock_llm

        result = run_interviewer(base_state)

    assert result["interview_round"] == 1


def test_interviewer_adds_ai_message(base_state):
    """인터뷰어 노드는 AI 메시지를 messages에 추가해야 한다"""
    mock_result = MagicMock()
    mock_result.question = "누가 이 서비스를 사용하나요?"
    mock_result.target_field = "target_persona"
    mock_result.reasoning = "페르소나 미수집"

    with patch("graph.nodes.interviewer._build_llm") as mock_build:
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = mock_result
        mock_build.return_value = mock_llm

        result = run_interviewer(base_state)

    assert len(result["messages"]) == 1
    assert isinstance(result["messages"][0], AIMessage)
    assert "누가" in result["messages"][0].content


def test_interviewer_multiple_rounds(base_state):
    """5라운드까지 진행 시 interview_round가 올바르게 누적돼야 한다"""
    mock_result = MagicMock()
    mock_result.question = "테스트 질문"
    mock_result.target_field = "edge_cases"
    mock_result.reasoning = "테스트"

    state = dict(base_state)
    state["interview_round"] = 3

    with patch("graph.nodes.interviewer._build_llm") as mock_build:
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = mock_result
        mock_build.return_value = mock_llm

        result = run_interviewer(state)

    assert result["interview_round"] == 4
