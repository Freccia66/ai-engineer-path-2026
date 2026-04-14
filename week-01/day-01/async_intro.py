# week-01/day-01/async_intro.py
# Async puro — pattern base per pipeline LLM

import asyncio
import time


async def fetch_data(task_id: int, delay: float) -> dict:
    """Simula una chiamata I/O (es. API call) con latenza variabile."""
    print(f"[{task_id}] start — attendo {delay:.1f}s")
    await asyncio.sleep(delay)
    print(f"[{task_id}] done")
    return {"task_id": task_id, "delay": delay}


async def main() -> None:
    # Pattern 1: sequenziale (SBAGLIATO per pipeline LLM)
    await main_error_handling()
    print("--- SEQUENZIALE ---")
    start = time.perf_counter()
    for i, delay in enumerate([1.0, 0.5, 0.8]):
        await fetch_data(i, delay)
    print(f"Tempo totale: {time.perf_counter() - start:.2f}s\n")

    # Pattern 2: parallelo con gather (GIUSTO)
    print("--- PARALLELO ---")
    start = time.perf_counter()
    results = await asyncio.gather(
        fetch_data(0, 1.0),
        fetch_data(1, 0.5),
        fetch_data(2, 0.8),
    )
    print(f"Tempo totale: {time.perf_counter() - start:.2f}s")
    print(f"Results: {results}")


async def fetch_with_error(task_id: int, should_fail: bool) -> dict:
    await asyncio.sleep(0.3)
    if should_fail:
        raise ValueError(f"[{task_id}] API timeout simulato")
    return {"task_id": task_id, "status": "ok"}


async def main_error_handling() -> None:
    print("\n--- GATHER CON return_exceptions ---")
    results = await asyncio.gather(
        fetch_with_error(0, should_fail=False),
        fetch_with_error(1, should_fail=True),
        fetch_with_error(2, should_fail=False),
        return_exceptions=True,
    )
    for r in results:
        if isinstance(r, Exception):
            print(f"Errore gestito: {r}")
        else:
            print(f"Successo: {r}")


if __name__ == "__main__":
    asyncio.run(main())
