from typing import List, Dict, Any, Optional
import json, re
from langchain_ollama import OllamaLLM

SYSTEM_PROMPT = """You are an electronics requirements assistant for PCB, IC, embedded hardware, and product design.
Your job is to collect complete and useful requirements through a natural conversation, one question at a time.

Goals
1) Greet briefly, then ask one thoughtful follow-up per turn.
2) Adapt to what the user already said. No fixed questionnaire. Avoid repeating answered items.
3) If the user lacks domain knowledge, propose options and examples, but do not invent specs. Ask to confirm assumptions.
4) Stay strictly in electronics/product requirements. If off-topic or inappropriate, politely redirect and set status OFF_TOPIC.
5) When requirements seem sufficient OR the user requests a human, set status COMPLETE or HUMAN_HANDOFF and produce a concise structured summary.

Output protocol
Respond as a single compact JSON object only:
{
  "assistant_message": string,
  "status": "ONGOING" | "COMPLETE" | "HUMAN_HANDOFF" | "OFF_TOPIC",
  "collected_fields": object,
  "ask_followup": boolean
}

Rules
- One question at a time while ONGOING.
- Keep messages short and specific. Use bullets only when summarizing.
- Cite documents only if provided in Context (e.g., [doc: PRD_XYZ.pdf]).
- If you cannot proceed, ask the most clarifying question next instead of guessing.
"""

def _format_history(history: List[Dict[str, str]]) -> str:
    if not history:
        return "ASSISTANT: Hi."
    lines = []
    for m in history[-24:]:
        role = m.get("role", "user").upper()
        content = m.get("content", "")
        lines.append(f"{role}: {content}")
    return "\n".join(lines)

def _format_known_slots(slots: Dict[str, Any]) -> str:
    if not slots:
        return "None"
    return "\n".join(f"- {k}: {v}" for k, v in slots.items())

def _extract_json(s: str) -> Optional[dict]:
    try:
        return json.loads(s)
    except Exception:
        pass
    m = re.search(r"\{.*\}", s, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(0))
        except Exception:
            return None
    return None

class ConversationEngine:
    def __init__(self, model_name: str = "tinyllama", temperature: float = 0.2):
        self.llm = OllamaLLM(model=model_name, temperature=temperature)

    def run_turn(
        self,
        history: List[Dict[str, str]],
        latest_user: str,
        known_slots: Dict[str, Any],
    ) -> Dict[str, Any]:
        transcript = _format_history(history)
        known = _format_known_slots(known_slots or {})

        user_block = f"User said:\n{latest_user}\n\nKnown so far:\n{known}\n"
        prompt = f"{SYSTEM_PROMPT}\n\nTranscript:\n{transcript}\n\n{user_block}\n\nOutput JSON only."

        try:
            raw = self.llm.invoke(prompt)
            parsed = _extract_json(raw or "")
        except Exception as e:
            return {
                "assistant_message": "I'm having trouble connecting to the AI model. Please make sure Ollama is running with the tinyllama model.",
                "status": "ONGOING",
                "collected_fields": {},
                "ask_followup": True,
            }

        if not isinstance(parsed, dict):
            return {
                "assistant_message": "Could you share one more detail, e.g. power source, interfaces, size, or environment?",
                "status": "ONGOING",
                "collected_fields": {},
                "ask_followup": True,
            }

        msg = (parsed.get("assistant_message") or "").strip()
        status = str(parsed.get("status") or "ONGOING").upper()
        fields = parsed.get("collected_fields") or {}
        ask = bool(parsed.get("ask_followup", True))

        return {
            "assistant_message": msg or "Can you clarify more about your project?",
            "status": status if status in {"ONGOING","COMPLETE","HUMAN_HANDOFF","OFF_TOPIC"} else "ONGOING",
            "collected_fields": fields if isinstance(fields, dict) else {},
            "ask_followup": ask,
        }
