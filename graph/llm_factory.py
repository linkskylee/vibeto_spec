"""
LLM Factory — 중앙 집중식 LLM 생성 유틸리티

사용 모델 우선순위:
  1. .env의 GEMINI_MODEL (기본: gemini-2.5-flash)
  2. 실패 시 자동 폴백: gemini-2.5-pro
"""
import os
import logging
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

logger = logging.getLogger(__name__)

# 폴백 순서: 기본 모델 → 안정 모델
_PRIMARY_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
_FALLBACK_MODEL = "gemini-2.5-pro"


def build_llm(temperature: float = 0.3, structured_output=None) -> ChatGoogleGenerativeAI:
    """
    LLM 인스턴스 생성. 기본 모델 실패 시 폴백 모델로 자동 전환.

    Args:
        temperature: 생성 온도
        structured_output: Pydantic 스키마 (with_structured_output 사용 시)

    Returns:
        ChatGoogleGenerativeAI 인스턴스 (structured_output 지정 시 래핑된 체인)
    """
    for model_name in [_PRIMARY_MODEL, _FALLBACK_MODEL]:
        try:
            llm = ChatGoogleGenerativeAI(
                model=model_name,
                temperature=temperature,
            )
            if structured_output is not None:
                chain = llm.with_structured_output(structured_output)
                # 실제 호출 가능 여부를 확인하기 위해 간단한 테스트는 생략
                # (모델 가용성은 첫 invoke 시 확인됨)
                logger.info(f"LLM initialized with model: {model_name}")
                return chain
            logger.info(f"LLM initialized with model: {model_name}")
            return llm
        except Exception as e:
            if model_name == _FALLBACK_MODEL:
                raise RuntimeError(
                    f"모든 모델 초기화 실패. 마지막 오류: {e}"
                ) from e
            logger.warning(
                f"모델 '{model_name}' 초기화 실패, '{_FALLBACK_MODEL}'로 폴백합니다. 오류: {e}"
            )
    # 도달 불가 (위 루프에서 raise)
    raise RuntimeError("LLM 초기화 실패")


def build_llm_with_fallback_invoke(messages: list, schema, temperature: float = 0.3):
    """
    invoke 시점에 폴백을 적용하는 안전한 LLM 호출.
    초기화는 성공해도 실제 API 호출에서 모델 미지원 에러가 날 수 있어
    invoke까지 포함한 폴백을 제공합니다.

    Args:
        messages: LangChain 메시지 리스트
        schema: Pydantic 구조화 출력 스키마
        temperature: 생성 온도

    Returns:
        schema 타입의 structured output 결과
    """
    for model_name in [_PRIMARY_MODEL, _FALLBACK_MODEL]:
        try:
            llm = ChatGoogleGenerativeAI(model=model_name, temperature=temperature)
            chain = llm.with_structured_output(schema)
            result = chain.invoke(messages)
            if model_name != _PRIMARY_MODEL:
                logger.warning(f"폴백 모델 '{model_name}' 사용됨")
            return result
        except Exception as e:
            error_str = str(e)
            # 모델 미지원 / 권한 오류일 때만 폴백, 나머지 오류는 그대로 raise
            if model_name == _FALLBACK_MODEL:
                raise
            if any(code in error_str for code in ["NOT_FOUND", "PERMISSION_DENIED", "404", "403"]):
                logger.warning(
                    f"모델 '{model_name}' 호출 실패 (오류: {e}), "
                    f"'{_FALLBACK_MODEL}'로 폴백합니다."
                )
                continue
            raise  # 다른 종류의 오류는 폴백 없이 즉시 전파
