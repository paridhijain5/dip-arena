from __future__ import annotations

from typing import Any, Dict, List

from .models import AgentKind, AgentResponse, Task


class BaseAgent:
    name: AgentKind

    def __init__(self, knowledge_base: Dict[str, List[str]]) -> None:
        self.knowledge_base = knowledge_base

    def run(self, task: Task, context: Dict[str, Any]) -> AgentResponse:
        raise NotImplementedError

    def _evidence_for_domain(self, task: Task, fallback: str) -> List[str]:
        return self.knowledge_base.get(task.domain, [fallback])


class ResearchAgent(BaseAgent):
    name = "research"

    def run(self, task: Task, context: Dict[str, Any]) -> AgentResponse:
        evidence = self._evidence_for_domain(task, "No domain evidence available.")
        return AgentResponse(
            agent_name="Research Agent",
            stance="Use evidence-backed reasoning and collect missing facts before finalizing.",
            claims=[
                "The decision should be grounded in available evidence rather than intuition.",
                "Independent reasoning helps reveal conflicting interpretations.",
            ],
            evidence=evidence[:2],
            assumptions=["The retrieved evidence is relevant to the user's question."],
            confidence=0.82,
            risks=["Incomplete evidence may bias the conclusion."],
            open_questions=["What evidence is missing?", "Which claim is most uncertain?"],
        )


class RiskAgent(BaseAgent):
    name = "risk"

    def run(self, task: Task, context: Dict[str, Any]) -> AgentResponse:
        evidence = self._evidence_for_domain(task, "No risk-specific evidence available.")
        return AgentResponse(
            agent_name="Risk Agent",
            stance="Delay commitment until major failure modes are enumerated.",
            claims=[
                "A fast answer can hide operational or downstream risks.",
                "Confidence should be discounted when evidence coverage is incomplete.",
            ],
            evidence=evidence[:2],
            assumptions=["Hidden failures are costly in this decision context."],
            confidence=0.88,
            risks=["Overconservative recommendations may reduce usefulness."],
            open_questions=["What is the worst plausible failure?", "What happens if the recommendation is wrong?"],
        )


class EthicsAgent(BaseAgent):
    name = "ethics"

    def run(self, task: Task, context: Dict[str, Any]) -> AgentResponse:
        evidence = self._evidence_for_domain(task, "No ethics-specific evidence available.")
        return AgentResponse(
            agent_name="Ethics Agent",
            stance="Prefer the option with the clearest harm minimization and stakeholder fairness.",
            claims=[
                "The recommendation should avoid unfair or harmful side effects.",
                "Stakeholder impact should be explicit, not implicit.",
            ],
            evidence=evidence[:2],
            assumptions=["The decision has meaningful impact on people or institutions."],
            confidence=0.79,
            risks=["Ethical framing can be too broad without concrete criteria."],
            open_questions=["Who bears the cost?", "Who benefits and who is excluded?"],
        )


class PolicyAgent(BaseAgent):
    name = "policy"

    def run(self, task: Task, context: Dict[str, Any]) -> AgentResponse:
        evidence = self._evidence_for_domain(task, "No policy-specific evidence available.")
        return AgentResponse(
            agent_name="Policy Agent",
            stance="Choose the path that is easiest to govern, audit, and explain.",
            claims=[
                "The recommendation should align with applicable policy or compliance constraints.",
                "A staged rollout is safer when regulation or governance is unclear.",
            ],
            evidence=evidence[:2],
            assumptions=["A governance mechanism exists or can be created."],
            confidence=0.76,
            risks=["Policy constraints may evolve faster than the system."],
            open_questions=["What regulations apply?", "What audit trail is required?"],
        )


class EconomicsAgent(BaseAgent):
    name = "economics"

    def run(self, task: Task, context: Dict[str, Any]) -> AgentResponse:
        evidence = self._evidence_for_domain(task, "No economics-specific evidence available.")
        return AgentResponse(
            agent_name="Economics Agent",
            stance="Prefer the option with the best long-run cost-benefit profile.",
            claims=[
                "The recommendation should consider total cost, not just immediate benefit.",
                "Second-order effects can dominate the short-term outcome.",
            ],
            evidence=evidence[:2],
            assumptions=["Cost and benefit can be estimated with reasonable accuracy."],
            confidence=0.74,
            risks=["Economic estimates can be very sensitive to assumptions."],
            open_questions=["What are the direct costs?", "What are the externalities?"],
        )


class StrategyAgent(BaseAgent):
    name = "strategy"

    def run(self, task: Task, context: Dict[str, Any]) -> AgentResponse:
        evidence = self._evidence_for_domain(task, "No strategy-specific evidence available.")
        return AgentResponse(
            agent_name="Strategy Agent",
            stance="Select the option that is most coherent with the long-term objective.",
            claims=[
                "The recommendation should align with the broader goal and execution capacity.",
                "A visible decision process increases trust in high-stakes settings.",
            ],
            evidence=evidence[:2],
            assumptions=["The objective is stable enough to optimize against."],
            confidence=0.8,
            risks=["A strategically elegant decision can still fail operationally."],
            open_questions=["What is the long-term objective?", "What capability limits exist?"],
        )