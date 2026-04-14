# week-01/day-01/structured_output.py
# Structured output con Anthropic API — pattern base per pipeline LLM

import asyncio
import json
import os

import anthropic
from dotenv import load_dotenv

load_dotenv()


async def extract_structured(text: str) -> dict:
    client = anthropic.AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    prompt = f"""Estrai le informazioni dal seguente testo e restituisci SOLO un JSON valido,
nessun testo aggiuntivo, nessun markdown.

Schema richiesto:
{{
  "company": "nome azienda",
  "amount": numero_float,
  "currency": "EUR|USD|GBP",
  "deadline": "YYYY-MM-DD o null",
  "service_type": "stringa descrittiva"
}}

Testo:
{text}"""

    message = await client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=256,
        messages=[
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": "{"},
        ],
    )

    raw = "{" + message.content[0].text
    print(f"RAW: {repr(raw)}")
    return json.loads(raw)


async def main() -> None:
    samples = [
        "Offerta da Accenture per consulenza ERP: 45.000 euro, consegna entro 30 giugno 2026.",
        "RFP risposta di Deloitte — servizi di audit finanziario, budget USD 120000, scadenza 2026-09-15.",
        "Preventivo McKinsey per analisi supply chain: 85.000 EUR, timeline non specificata.",
    ]

    results = await asyncio.gather(
        *[extract_structured(s) for s in samples],
        return_exceptions=True,
    )

    for i, r in enumerate(results):
        if isinstance(r, Exception):
            print(f"[{i}] Errore: {r}")
        else:
            print(f"[{i}] {json.dumps(r, ensure_ascii=False, indent=2)}")


if __name__ == "__main__":
    asyncio.run(main())
