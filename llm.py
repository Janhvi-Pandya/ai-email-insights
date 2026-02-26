from __future__ import annotations

import os
import json
from typing import Optional, Dict, Any

from pydantic import BaseModel, Field

# OpenAI SDK (new style)
# pip install openai
try:
    from openai import OpenAI
except Exception:
    OpenAI = None


class EmailInsights(BaseModel):
    summary_bullets: list[str] = Field(..., description="3-6 bullet summary points")
    topic: str = Field(..., description="One of: operations, maintenance, customer_service, incident, asset_management, scheduling, other")
    urgency: str = Field(..., description="One of: low, medium, high")
    sentiment: str = Field(..., description="One of: negative, neutral, positive")
    action_items: list[str] = Field(..., description="Concrete action items, 0-6 items")
    entities: list[str] = Field(default_factory=list, description="Key entities like vessel name, terminal, equipment, dates")


SYSTEM_PROMPT = """You are an enterprise analytics assistant helping an IT/analytics team summarize operational emails.
Return structured JSON ONLY matching the provided schema.
Be concise, business-like, and avoid hallucinations: only use details present in the email.
If unknown, omit from entities.
Topics allowed: operations, maintenance, customer_service, incident, asset_management, scheduling, other.
Urgency: high if safety, incident, imminent deadline, or major customer impact; medium for time-sensitive but non-critical; low for informational.
Sentiment: negative for complaints/frustration; neutral for routine operations; positive for praise.
"""


def _offline_insights(subject: str, body: str) -> EmailInsights:
    text = f"{subject}\n{body}".lower()

    # Topic heuristic
    if any(k in text for k in ["hvac", "fault", "inspection", "parts", "maintenance", "repair", "vibration"]):
        topic = "maintenance"
    elif any(k in text for k in ["incident", "damage", "injur", "report", "safety"]):
        topic = "incident"
    elif any(k in text for k in ["lost", "refund", "complaint", "missed", "delay", "customer"]):
        topic = "customer_service"
    elif any(k in text for k in ["asset", "sensor", "baseline", "calibration"]):
        topic = "asset_management"
    elif any(k in text for k in ["schedule", "sailing", "delayed", "cancel"]):
        topic = "scheduling"
    else:
        topic = "operations"

    # Urgency heuristic
    urgency = "low"
    if any(k in text for k in ["injur", "safety", "incident", "urgent", "asap", "immediately"]):
        urgency = "high"
    elif any(k in text for k in ["prioritize", "before", "deadline", "long weekend", "soon"]):
        urgency = "medium"

    # Sentiment heuristic
    sentiment = "neutral"
    if any(k in text for k in ["complaint", "missed", "again", "frustrat", "unacceptable", "angry", "refund"]):
        sentiment = "negative"
    elif any(k in text for k in ["thank", "great", "appreciate"]):
        sentiment = "positive"

    # Summary bullets (very simple)
    bullets = []
    if subject.strip():
        bullets.append(f"Subject: {subject.strip()}")
    body_clean = " ".join(body.strip().split())
    if body_clean:
        bullets.append(body_clean[:180] + ("…" if len(body_clean) > 180 else ""))

    # Action items heuristic
    actions = []
    if "request" in text or "recommend" in text or "please" in text:
        actions.append("Review email details and determine next steps.")
    if topic == "incident":
        actions.append("Log the incident and notify relevant supervisor/stakeholders.")
    if topic == "maintenance":
        actions.append("Schedule inspection and assess parts/resources needed.")
    if topic == "customer_service":
        actions.append("Respond to customer with status, explanation, and next steps.")

    return EmailInsights(
        summary_bullets=bullets[:6],
        topic=topic,
        urgency=urgency,
        sentiment=sentiment,
        action_items=actions[:6],
        entities=[],
    )


def generate_insights(subject: str, body: str, model: str = "gpt-4o-mini") -> EmailInsights:
    """
    Uses OpenAI if OPENAI_API_KEY is present; otherwise offline fallback.
    """
    api_key = os.getenv("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", "").strip()
    if not api_key or OpenAI is None:
        return _offline_insights(subject, body)

    client = OpenAI(api_key=api_key)

    schema = EmailInsights.model_json_schema()
    user_prompt = f"""
EMAIL SUBJECT:
{subject}

EMAIL BODY:
{body}

Return JSON that matches this JSON Schema:
{json.dumps(schema, indent=2)}
"""

    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
        response_format={"type": "json_object"},
    )

    content = resp.choices[0].message.content
    data: Dict[str, Any] = json.loads(content)
    return EmailInsights.model_validate(data)