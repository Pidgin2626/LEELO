"""Drive the 3-round panel debate.

Round 1: each advisor answers independently (parallel).
Round 2: each advisor sees the others' answers and critiques them (parallel).
Round 3: synthesizer reads everything and produces a verdict (one call).
"""

from __future__ import annotations

import concurrent.futures
from dataclasses import dataclass, field

import click

from .personas import (
    PERSONAS,
    ROUND_1_TEMPLATE,
    ROUND_2_TEMPLATE,
    SYNTHESIZER_TEMPLATE,
    Persona,
)
from .providers import Advisor, AnthropicAdvisor


@dataclass
class Seat:
    advisor: Advisor
    persona: Persona
    round_1: str = ""
    round_2: str = ""


@dataclass
class CouncilResult:
    question: str
    seats: list[Seat] = field(default_factory=list)
    synthesis: str = ""
    transcript_md: str = ""


def _assign_personas(advisors: list[Advisor]) -> list[Seat]:
    """Hand each advisor a persona. Advisors > 5 wrap; advisors < 5 use first N."""
    persona_keys = list(PERSONAS.keys())
    seats: list[Seat] = []
    for i, adv in enumerate(advisors):
        key = persona_keys[i % len(persona_keys)]
        seats.append(Seat(advisor=adv, persona=PERSONAS[key]))
    return seats


def _round_1(seats: list[Seat], question: str) -> None:
    click.secho("\n>>> Round 1: independent answers", fg="cyan", bold=True)

    def run(seat: Seat) -> tuple[Seat, str]:
        prompt = ROUND_1_TEMPLATE.format(
            name=seat.persona.name,
            lens=seat.persona.lens,
            question=question,
        )
        click.echo(f"  asking {seat.advisor.name} ({seat.persona.name}) ...")
        text = seat.advisor.ask(seat.persona.system_prompt, prompt, max_tokens=1500)
        return seat, text

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(seats)) as ex:
        for seat, text in ex.map(run, seats):
            seat.round_1 = text
            click.secho(f"  {seat.advisor.name} done.", fg="green")


def _round_2(seats: list[Seat], question: str) -> None:
    click.secho("\n>>> Round 2: peer critique", fg="cyan", bold=True)

    def run(seat: Seat) -> tuple[Seat, str]:
        others = [
            f"### {s.advisor.name} ({s.persona.name})\n{s.round_1}"
            for s in seats
            if s is not seat
        ]
        prompt = ROUND_2_TEMPLATE.format(
            name=seat.persona.name,
            lens=seat.persona.lens,
            question=question,
            other_answers="\n\n".join(others),
        )
        click.echo(f"  {seat.advisor.name} reviewing the others ...")
        text = seat.advisor.ask(seat.persona.system_prompt, prompt, max_tokens=2000)
        return seat, text

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(seats)) as ex:
        for seat, text in ex.map(run, seats):
            seat.round_2 = text
            click.secho(f"  {seat.advisor.name} done.", fg="green")


def _build_transcript(question: str, seats: list[Seat]) -> str:
    parts: list[str] = [f"# Question\n\n{question}\n\n# Round 1: independent answers\n"]
    for seat in seats:
        parts.append(
            f"## {seat.advisor.name} — {seat.persona.name}\n\n{seat.round_1}\n"
        )
    parts.append("# Round 2: peer critique\n")
    for seat in seats:
        parts.append(
            f"## {seat.advisor.name} critiquing the panel\n\n{seat.round_2}\n"
        )
    return "\n".join(parts)


def _synthesize(question: str, transcript: str) -> str:
    click.secho("\n>>> Round 3: synthesis", fg="cyan", bold=True)
    synth = AnthropicAdvisor()
    if not synth.available:
        return "(synthesizer unavailable — set ANTHROPIC_API_KEY to enable)"
    return synth.ask(
        system=(
            "You synthesize the output of multi-advisor decision panels. "
            "Be decisive but honest about uncertainty."
        ),
        user=SYNTHESIZER_TEMPLATE.format(question=question, transcript=transcript),
        max_tokens=2500,
    )


def run_council(question: str, advisors: list[Advisor]) -> CouncilResult:
    seats = _assign_personas(advisors)
    _round_1(seats, question)
    _round_2(seats, question)
    transcript = _build_transcript(question, seats)
    synthesis = _synthesize(question, transcript)

    return CouncilResult(
        question=question,
        seats=seats,
        synthesis=synthesis,
        transcript_md=transcript,
    )


def render_full(result: CouncilResult) -> str:
    return (
        f"# Verdict\n\n{result.synthesis}\n\n"
        f"---\n\n# Full transcript\n\n{result.transcript_md}"
    )
