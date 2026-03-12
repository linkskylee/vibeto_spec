"""
Spec Generator Node — Phase 3
도메인 맵과 인터뷰 내용을 바탕으로 Agent-ready 스펙 문서를 생성합니다.
"""
import json
from pathlib import Path
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

from graph.state import GraphState
from schemas.spec import FinalSpec

_PROMPT_PATH = Path(__file__).parent.parent.parent / "prompts" / "spec_generator_system.md"
_SYSTEM_PROMPT = _PROMPT_PATH.read_text(encoding="utf-8")


def _build_llm():
    from dotenv import load_dotenv
    load_dotenv()
    import os
    llm = ChatGoogleGenerativeAI(
        model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
        temperature=0.1,
    )
    return llm.with_structured_output(FinalSpec)


def _spec_to_markdown(spec: FinalSpec) -> str:
    """FinalSpec Pydantic 모델을 마크다운 문자열로 변환"""
    ctx = spec.context
    task = spec.task
    test = spec.test

    md = f"""# {ctx.project_name} — Agent-ready Spec

## 📋 1. Context (프로젝트 배경)

**배경**: {ctx.background}

**대상 사용자**: {ctx.target_persona}

**기술 스택**:
{chr(10).join(f"- {t}" for t in ctx.tech_stack)}

**제약 사항**:
{chr(10).join(f"- {c}" for c in ctx.constraints)}

---

## 🎯 2. Task (구현 요청)

**목표**: {task.objective}

**핵심 엔티티**:
{chr(10).join(f"- `{e}`" for e in task.domain_entities)}

**구현할 기능 (Actions)**:
{chr(10).join(f"- `{a}`" for a in task.actions)}

**비즈니스 규칙** (반드시 구현):
{chr(10).join(f"{i+1}. {r}" for i, r in enumerate(task.business_rules))}

**예외 처리 (Edge Cases)**:
{chr(10).join(f"- {e}" for e in task.edge_cases)}

**권장 폴더 구조**:
```
{task.folder_structure}
```

---

## ✅ 3. Test (검증 체크리스트)

**성공 기준**:
{chr(10).join(f"- [ ] {s}" for s in test.success_criteria)}

**테스트 시나리오**:
{chr(10).join(f"{i+1}. {s}" for i, s in enumerate(test.test_scenarios))}

**최종 승인 조건**:
{chr(10).join(f"- [ ] {a}" for a in test.acceptance_conditions)}

---
*예상 토큰 수: {spec.token_estimate} tokens*
"""
    return md


def run_spec_generator(state: GraphState) -> dict:
    """
    스펙 생성 노드.
    인터뷰 + 도메인 맵을 종합해 최종 스펙 마크다운을 생성합니다.
    """
    llm = _build_llm()

    conversation_text = "\n".join([
        f"{msg.type.upper()}: {msg.content}"
        for msg in state.get("messages", [])
    ])
    domain_map = state.get("domain_map", {})
    improvement_hints = state.get("_improvement_hints", [])  # 재생성 시 품질 검토 피드백

    improvement_section = ""
    if improvement_hints:
        improvement_section = f"""
[이전 스펙의 개선 필요 사항 - 반드시 반영하세요]
{chr(10).join(f"- {h}" for h in improvement_hints)}
"""

    messages_for_llm = [
        SystemMessage(content=_SYSTEM_PROMPT),
        HumanMessage(content=f"""[인터뷰 내용]
{conversation_text}

[도메인 맵]
{json.dumps(domain_map, ensure_ascii=False, indent=2)}
{improvement_section}
위 정보를 바탕으로 완전한 Agent-ready 스펙 문서를 작성해 주세요."""),
    ]

    result: FinalSpec = llm.invoke(messages_for_llm)
    markdown_spec = _spec_to_markdown(result)

    # 토큰 수 추정: 문자 수 / 4 (영어 기준 근사치)
    raw_text = "\n".join([msg.content for msg in state.get("messages", [])])
    raw_token_estimate = len(raw_text) // 4
    spec_token_estimate = len(markdown_spec) // 4

    return {
        "final_spec": markdown_spec,
        "raw_token_count": raw_token_estimate,
        "spec_token_count": spec_token_estimate,
        "spec_regeneration_count": state.get("spec_regeneration_count", 0),
    }
