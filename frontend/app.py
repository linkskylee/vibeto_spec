"""
Streamlit 채팅 UI
FastAPI 백엔드와 통신해 인터뷰 → 스펙 생성 흐름을 시각화합니다.
"""
import streamlit as st
import httpx
import json

# ── 설정 ─────────────────────────────────────────────────────────
API_BASE = "http://localhost:8000/api"

st.set_page_config(
    page_title="Vibe-to-Spec | 프롬프트 아키텍트",
    page_icon="🧠",
    layout="wide",
)

# ── 상태 초기화 ───────────────────────────────────────────────────
if "thread_id" not in st.session_state:
    st.session_state.thread_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "phase" not in st.session_state:
    st.session_state.phase = "interviewing"
if "completeness_score" not in st.session_state:
    st.session_state.completeness_score = 0.0
if "final_spec" not in st.session_state:
    st.session_state.final_spec = None
if "token_stats" not in st.session_state:
    st.session_state.token_stats = None
if "checklist" not in st.session_state:
    st.session_state.checklist = {}

# ── 사이드바 ──────────────────────────────────────────────────────
with st.sidebar:
    st.title("🧠 Vibe-to-Spec")
    st.caption("막연한 아이디어를 AI가 실행할 수 있는 스펙으로 변환합니다.")
    st.divider()

    # Phase 진행 상태 표시
    phase_map = {
        "interviewing": ("🎤 인터뷰 중", "blue"),
        "translating": ("🗺️ 도메인 분석 중", "orange"),
        "generating": ("📝 스펙 생성 중", "orange"),
        "done": ("✅ 완료!", "green"),
    }
    phase_label, phase_color = phase_map.get(st.session_state.phase, ("...", "gray"))
    st.metric("현재 단계", phase_label)

    # 완료도 프로그레스바
    st.write("**요구사항 수집 완료도**")
    st.progress(st.session_state.completeness_score)
    st.caption(f"{st.session_state.completeness_score * 100:.0f}%")

    # 체크리스트 시각화
    st.divider()
    st.write("**📋 수집 현황**")

    CHECKLIST_LABELS = {
        "project_goal":    ("🚀", "프로젝트 목적"),
        "target_persona":  ("👤", "대상 사용자"),
        "business_rules":  ("⚙️", "핵심 기능/규칙"),
        "data_flow":       ("🔄", "데이터 흐름"),
        "constraints":     ("🔒", "기술·제약 사항"),
        "edge_cases":      ("⚠️", "예외 처리"),
    }

    checklist = st.session_state.checklist
    if not checklist:
        st.caption("첫 메시지를 보내면 분석이 시작됩니다.")
    else:
        for key, (emoji, label) in CHECKLIST_LABELS.items():
            done = checklist.get(key, False)
            icon = "✅" if done else "⬜"
            color = "normal" if done else "off"
            st.markdown(f"{icon} {emoji} **{label}**" if done else f"{icon} {emoji} {label}")

    if st.session_state.token_stats:
        st.divider()
        st.write("**📊 토큰 분석**")
        stats = st.session_state.token_stats
        col1, col2 = st.columns(2)
        col1.metric("원본", f"{stats['raw_tokens']} tok")
        col2.metric("스펙", f"{stats['spec_tokens']} tok")
        st.success(f"최적화율: {stats['efficiency']}")

    st.divider()
    if st.button("🔄 새 대화 시작", use_container_width=True):
        st.session_state.thread_id = None
        st.session_state.messages = []
        st.session_state.phase = "interviewing"
        st.session_state.completeness_score = 0.0
        st.session_state.final_spec = None
        st.session_state.token_stats = None
        st.session_state.checklist = {}
        st.rerun()

# ── 메인 영역 ─────────────────────────────────────────────────────
st.title("💬 프롬프트 아키텍트")

# 환영 메시지 (첫 방문)
if not st.session_state.messages:
    with st.chat_message("assistant"):
        st.write("""안녕하세요! 저는 여러분의 **아이디어를 AI가 실행할 수 있는 스펙 문서로 변환**해 드리는 프롬프트 아키텍트입니다. 🚀

만들고 싶은 것을 자유롭게 말씀해 주세요. 몇 가지 질문을 통해 더 명확한 스펙을 만들어 드릴게요!

**예시:** "쇼핑몰 앱 만들고 싶어요" / "할 일 관리 앱 개발 중인데 스펙 정리가 필요해요"
""")

# 기존 대화 메시지 표시
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 스펙 완성 시 별도 표시
if st.session_state.final_spec:
    with st.expander("📄 완성된 스펙 문서 보기 (클릭하여 펼치기)", expanded=True):
        st.markdown(st.session_state.final_spec)
        st.download_button(
            label="⬇️ 스펙 문서 다운로드 (.md)",
            data=st.session_state.final_spec,
            file_name="vibe_to_spec_output.md",
            mime="text/markdown",
        )

# ── 채팅 입력 ─────────────────────────────────────────────────────
if st.session_state.phase != "done":
    if user_input := st.chat_input("아이디어를 입력하세요..."):
        # 사용자 메시지 표시
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        # API 호출
        with st.chat_message("assistant"):
            with st.spinner("분석 중..."):
                try:
                    response = httpx.post(
                        f"{API_BASE}/chat/message",
                        json={
                            "message": user_input,
                            "thread_id": st.session_state.thread_id,
                        },
                        timeout=120.0,
                    )
                    response.raise_for_status()
                    data = response.json()

                    # 상태 업데이트
                    st.session_state.thread_id = data["thread_id"]
                    st.session_state.phase = data["phase"]
                    st.session_state.completeness_score = data["completeness_score"]
                    st.session_state.checklist = data.get("checklist", {})

                    if data.get("final_spec"):
                        st.session_state.final_spec = data["final_spec"]

                    if data.get("token_stats"):
                        st.session_state.token_stats = data["token_stats"]

                    # AI 응답 표시
                    reply = data["reply"]
                    st.write(reply)
                    st.session_state.messages.append({"role": "assistant", "content": reply})

                    if data["phase"] == "done":
                        st.success("🎉 스펙 문서가 완성됐습니다! 왼쪽 사이드바에서 토큰 분석을 확인하세요.")

                    st.rerun()

                except httpx.ConnectError:
                    st.error("⚠️ FastAPI 서버에 연결할 수 없습니다. `uvicorn api.main:app --reload` 명령어로 서버를 먼저 시작해 주세요.")
                except Exception as e:
                    st.error(f"오류 발생: {str(e)}")
else:
    st.chat_input("스펙이 완성됐습니다. '새 대화 시작'을 눌러 다시 시작하세요.", disabled=True)
