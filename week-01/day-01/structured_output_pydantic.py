# week-01/day-01/structured_output_pydantic.py
# Structured output con Pydantic validation

import asyncio
import json
import os
from typing import Literal

import anthropic
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError

load_dotenv()


class RFPExtraction(BaseModel):
    company: str
    amount: float
    currency: Literal["EUR", "USD", "GBP"]
    deadline: str | None
    service_type: str


async def extract_structured(text: str) -> RFPExtraction:
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
    data = json.loads(raw)
    return RFPExtraction(**data)


async def main() -> None:
    samples = [
        "Offerta da Accenture per consulenza ERP: 45.000 euro, consegna entro 30 giugno 2026.",
        "RFP risposta di Deloitte — servizi di audit finanziario, budget USD 120000, scadenza 2026-09-15.",
        "Preventivo McKinsey per analisi supply chain: 85.000 EUR, timeline non specificata.",
        "Offerta KPMG per revisione contabile: budget 'da definire', valuta sterline.",  # edge case
    ]

    results = await asyncio.gather(
        *[extract_structured(s) for s in samples],
        return_exceptions=True,
    )

    for i, r in enumerate(results):
        if isinstance(r, ValidationError):
            print(f"[{i}] Validation error: {r.errors()}")
        elif isinstance(r, Exception):
            print(f"[{i}] Errore: {r}")
        else:
            print(f"[{i}] {r.model_dump_json(indent=2)}")


if __name__ == "__main__":
    asyncio.run(main())
