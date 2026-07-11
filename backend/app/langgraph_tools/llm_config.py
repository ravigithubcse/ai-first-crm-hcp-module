# =============================================================================
# AI-First CRM HCP Module - LLM Configuration
# =============================================================================
# Author      : Ravi Kumar
# Date        : 2026-07-09
# Version     : 1.0.0
# Description : Groq LLM configuration for LangGraph agent
# Copyright (c) 2026. All rights reserved.
# =============================================================================

"""
LLM configuration using Groq API with gemma2-9b-it model.
Provides the language model instance for LangGraph tools.
"""

import os

from langchain_groq import ChatGroq
from app.core.config import settings


def get_llm(temperature: float = 0.3) -> ChatGroq:
    """
    Get a configured Groq LLM instance.

    Args:
        temperature: Sampling temperature (0.0 - 1.0)

    Returns:
        Configured ChatGroq instance
    """
    api_key = settings.groq_api_key or os.getenv("GROQ_API_KEY", "")

    if not api_key:
        raise ValueError(
            "Groq API key not configured. "
            "Set GROQ_API_KEY in environment or .env file."
        )

    return ChatGroq(
        model="gemma2-9b-it",
        temperature=temperature,
        groq_api_key=api_key,
        max_retries=3,
        timeout=30,
    )


def get_llm_with_context(temperature: float = 0.3) -> ChatGroq:
    """
    Get Groq LLM with larger context window using llama-3.3-70b.
    Use this for complex analysis requiring more context.
    """
    api_key = settings.groq_api_key or os.getenv("GROQ_API_KEY", "")

    if not api_key:
        raise ValueError(
            "Groq API key not configured. "
            "Set GROQ_API_KEY in environment or .env file."
        )

    return ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=temperature,
        groq_api_key=api_key,
        max_retries=3,
        timeout=30,
    )