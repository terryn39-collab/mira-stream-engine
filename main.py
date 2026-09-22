"""Mira Laurent real-time conversational stream backend."""

from __future__ import annotations

import re
from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(
    title="Mira Stream Engine",
    version="1.0.0",
    description="Backend adapter for Mira Laurent interactive video streams.",
)


class ChatInput(BaseModel):
    user_message: str = Field(..., min_length=1, max_length=2000)
    session_id: str = Field(..., min_length=1, max_length=128)


class WebRTCPayload(BaseModel):
    session_id: str
    transport: Literal["webrtc"] = "webrtc"
    event: Literal["avatar.speak"] = "avatar.speak"
    text: str
    persona: str = "mira-laurent-v1"
    provider: Literal["tavus", "anam", "generic"] = "generic"


def trim_to_word_limit(text: str, limit: int = 39) -> str:
    """Guarantee dialogue remains below 40 whitespace-delimited words."""
    words = text.split()
    return " ".join(words[:limit])


def mira_reply(user_message: str) -> str:
    """Deterministic local persona simulation; replace with an LLM call later."""
    clean = re.sub(r"\s+", " ", user_message).strip()
    lowered = clean.lower()

    if any(term in lowered for term in ("tokyo", "japan")):
        reply = (
            "Tokyo feels best when you leave space in the day. "
            "I’d choose a beautifully cut neutral look, one quiet coffee stop, "
            "then somewhere architectural before dinner."
        )
    elif any(term in lowered for term in ("paris", "france")):
        reply = (
            "Paris rewards simplicity. I’d wear something tailored, walk rather "
            "than over-plan, stop somewhere intimate for coffee, and let one "
            "beautiful place become the focus of the day."
        )
    elif any(term in lowered for term in ("wear", "outfit", "fashion", "style")):
        reply = (
            "I’d keep it restrained: cream, espresso or slate, beautiful fabric, "
            "clean tailoring and one considered accessory. The easiest luxury "
            "looks usually have fewer competing details."
        )
    elif any(term in lowered for term in ("hotel", "travel", "trip", "stay")):
        reply = (
            "I look for calm design, thoughtful service and a location that makes "
            "walking easy. A smaller beautiful room in the right neighborhood "
            "often feels more luxurious than excess."
        )
    else:
        reply = (
            "I’d approach it simply and choose the version that feels considered "
            "rather than excessive. Good design, useful details and a little "
            "spontaneity usually make the experience feel more memorable."
        )

    return trim_to_word_limit(reply)


def build_webrtc_payload(chat: ChatInput, reply: str) -> WebRTCPayload:
    """Map generated dialogue into a provider-neutral real-time avatar event."""
    return WebRTCPayload(
        session_id=chat.session_id,
        text=reply,
        provider="generic",
    )


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "persona": "mira-laurent-v1"}


@app.post("/stream/chat", response_model=WebRTCPayload)
async def stream_chat(chat: ChatInput) -> WebRTCPayload:
    reply = mira_reply(chat.user_message)
    return build_webrtc_payload(chat, reply)
