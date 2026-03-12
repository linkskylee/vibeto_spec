"""
Chat Route — 그래프와의 통신 엔드포인트

POST /api/chat/message  : 메시지 전송 → 다음 AI 질문 또는 스펙 반환
GET  /api/chat/spec/{thread_id} : 완성된 스펙 문서 조회
DELETE /api/chat/{thread_id}    : 세션 초기화
"""
import uuid
from fastapi import APIRouter
from pydantic import BaseModel
from langchain_core.messages import HumanMessage

from graph.builder import graph
from graph.state import GraphState

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str
    thread_id: str | None = None  # None이면 새 세션 생성


class ChatResponse(BaseModel):
    thread_id: str
    reply: str              # AI의 다음 질문 또는 완료 메시지
    phase: str              # "interviewing" | "translating" | "generating" | "done"
    completeness_score: float
    final_spec: str | None  # 스펙 완성 시에만 값 존재
    token_stats: dict | None


@router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """
    사용자 메시지를 받아 그래프를 실행하고 AI 응답을 반환합니다.
    thread_id로 대화 세션을 관리합니다.
    """
    # 새 세션이면 UUID 생성
    thread_id = request.thread_id or str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    # 그래프에 사용자 메시지 전달
    user_message = HumanMessage(content=request.message)

    # 현재 상태 조회 (체크포인터에서 복원)
    current_state = graph.get_state(config)
    is_new = current_state.values == {}

    # 초기 상태 설정 (신규 세션)
    if is_new:
        initial_state: GraphState = {
            "messages": [user_message],
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
        input_state = initial_state
    else:
        # 기존 세션: 메시지만 추가 (체크포인터가 나머지 상태 복원)
        input_state = {"messages": [user_message]}

    # 그래프 실행
    result_state = await graph.ainvoke(input_state, config=config)

    # 마지막 AI 메시지 추출
    messages = result_state.get("messages", [])
    ai_messages = [m for m in messages if hasattr(m, "type") and m.type == "ai"]
    last_reply = ai_messages[-1].content if ai_messages else "처리 중 오류가 발생했습니다."

    # 현재 Phase 판단
    final_spec = result_state.get("final_spec", "")
    quality_score = result_state.get("quality_score", 0.0)
    completeness = result_state.get("completeness_score", 0.0)

    if final_spec and quality_score >= 0.75:
        phase = "done"
    elif result_state.get("domain_map"):
        phase = "generating"
    elif completeness >= 0.8:
        phase = "translating"
    else:
        phase = "interviewing"

    # 토큰 절약 통계
    raw_tokens = result_state.get("raw_token_count", 0)
    spec_tokens = result_state.get("spec_token_count", 0)
    token_stats = None
    if raw_tokens > 0 and spec_tokens > 0:
        token_stats = {
            "raw_tokens": raw_tokens,
            "spec_tokens": spec_tokens,
            "efficiency": f"{(1 - spec_tokens / max(raw_tokens, 1)) * 100:.1f}%",
        }

    return ChatResponse(
        thread_id=thread_id,
        reply=last_reply,
        phase=phase,
        completeness_score=completeness,
        final_spec=final_spec if phase == "done" else None,
        token_stats=token_stats if phase == "done" else None,
    )


@router.delete("/{thread_id}")
async def reset_session(thread_id: str):
    """세션 초기화 (체크포인터에서 해당 thread 데이터 삭제)"""
    # MemorySaver는 명시적 삭제 API가 없으므로 새 thread_id 사용 안내
    return {"message": "새 thread_id로 시작하면 세션이 초기화됩니다.", "thread_id": thread_id}
