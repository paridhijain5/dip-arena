from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict
from typing import Any, Dict, Iterable, List, Optional
from uuid import uuid4

from .agents import EconomicsAgent, EthicsAgent, PolicyAgent, ResearchAgent, RiskAgent, StrategyAgent
from .models import AgentKind, AgentResponse, Critique, DecisionReport, Domain, Task, ValidationResult, ValidationStatus


class DIPOrchestrator:
    def __init__(self, knowledge_base: Optional[Dict[str, List[str]]] = None) -> None:
        self.knowledge_base = knowledge_base or {
            "policy": [
                "High-stakes policy decisions usually require review across multiple perspectives.",
                "Transparent reasoning supports auditability and governance.",
            ],
            "healthcare": [
                "Medical decisions benefit from second opinions and evidence review.",
                "Safety and harm reduction matter more than raw speed in critical care.",
            ],
            "business": [
                "Business strategy should weigh cost, risk, and execution constraints.",
                "Different functional perspectives reveal tradeoffs that single-shot answers miss.",
            ],
            "research": [
                "Peer review and adversarial critique improve reasoning quality.",
                "Evidence quality is as important as conclusion quality.",
            ],
            "security": [
                "Security decisions should assume adversarial conditions and hidden failure modes.",
                "Validation and threat modeling are essential before deployment.",
            ],
            "general": [
                "Structured disagreement can improve decision quality.",
                "Confidence should be lower when evidence is thin.",
            ],
        }
        self.agent_pool = {
            "research": ResearchAgent(self.knowledge_base),
            "risk": RiskAgent(self.knowledge_base),
            "ethics": EthicsAgent(self.knowledge_base),
            "policy": PolicyAgent(self.knowledge_base),
            "economics": EconomicsAgent(self.knowledge_base),
            "strategy": StrategyAgent(self.knowledge_base),
        }

    def decide(self, query: str, domain: Domain = "general", context: Optional[Dict[str, Any]] = None) -> DecisionReport:
        task = self._observe(query, domain, context or {})
        retrieved_context = self._retrieve_context(task)
        agent_outputs = self._run_agents(task, retrieved_context)
        critiques = self._challenge(task, agent_outputs)
        validations = self._validate(task, agent_outputs, retrieved_context)
        return self._synthesize(task, agent_outputs, critiques, validations)

    def _observe(self, query: str, domain: Domain, context: Dict[str, Any]) -> Task:
        constraints = context.get("constraints", [])
        if not isinstance(constraints, list):
            constraints = [str(constraints)]

        return Task(
            query_id=str(uuid4()),
            query_text=query,
            domain=domain,
            stakes=context.get("stakes", "medium"),
            constraints=constraints,
            required_agents=self._route_agents(domain, query),
            evidence_needed=["domain evidence", "risk assessment", "stakeholder impact", "validation sources"],
            context=context,
        )

    def _retrieve_context(self, task: Task) -> Dict[str, Any]:
        context_snippets = self.knowledge_base.get(task.domain, self.knowledge_base["general"])
        return {
            "task": asdict(task),
            "retrieved_evidence": context_snippets,
            "policy_constraints": task.constraints,
            "notes": task.context.get("notes", []),
            "mode": "free-local",
        }

    def _route_agents(self, domain: Domain, query: str) -> List[AgentKind]:
        normalized = query.lower()
        routed: List[AgentKind] = ["research", "risk", "strategy"]

        if domain in {"policy", "healthcare", "security", "research", "business"}:
            routed.append("ethics")
        if domain in {"policy", "business", "security"}:
            routed.append("policy")
        if domain in {"business", "policy", "general"} or any(keyword in normalized for keyword in ["cost", "budget", "pricing", "market"]):
            routed.append("economics")

        return list(dict.fromkeys(routed))

    def _run_agents(self, task: Task, context: Dict[str, Any]) -> List[AgentResponse]:
        agent_outputs: List[AgentResponse] = []
        with ThreadPoolExecutor(max_workers=len(task.required_agents)) as executor:
            futures = {executor.submit(self.agent_pool[agent_kind].run, task, context): agent_kind for agent_kind in task.required_agents}
            for future in as_completed(futures):
                agent_outputs.append(future.result())

        return sorted(agent_outputs, key=lambda response: response.agent_name)

    def _challenge(self, task: Task, agent_outputs: List[AgentResponse]) -> List[Critique]:
        critiques: List[Critique] = []
        if len(agent_outputs) < 2:
            return critiques

        strongest_confidence = max(agent_outputs, key=lambda response: response.confidence)
        weakest_confidence = min(agent_outputs, key=lambda response: response.confidence)

        if strongest_confidence.agent_name != weakest_confidence.agent_name:
            critiques.append(
                Critique(
                    target_agent=strongest_confidence.agent_name,
                    objection="High confidence may be masking unverified assumptions.",
                    severity="medium",
                    evidence_against=["No claim is fully validated until evidence is checked."],
                    unresolved_issue="Confidence should be discounted if supporting evidence is sparse.",
                )
            )

        for response in agent_outputs:
            if len(response.open_questions) > 1:
                critiques.append(
                    Critique(
                        target_agent=response.agent_name,
                        objection="The response identifies gaps but does not yet close them.",
                        severity="low",
                        evidence_against=["Open questions indicate incomplete coverage."],
                        unresolved_issue=response.open_questions[0],
                    )
                )

        return critiques

    def _validate(self, task: Task, agent_outputs: List[AgentResponse], context: Dict[str, Any]) -> List[ValidationResult]:
        source_pool = context.get("retrieved_evidence", self.knowledge_base.get(task.domain, []))
        validations: List[ValidationResult] = []

        for agent_index, agent_response in enumerate(agent_outputs):
            for claim_index, claim in enumerate(agent_response.claims):
                source, status, confidence, notes = self._score_claim(claim, source_pool, agent_response.confidence)
                validations.append(
                    ValidationResult(
                        claim_id=f"{agent_index}:{claim_index}",
                        claim=claim,
                        status=status,
                        source=source,
                        confidence=confidence,
                        notes=notes,
                    )
                )

        return validations

    def _score_claim(self, claim: str, source_pool: Iterable[str], agent_confidence: float) -> tuple[str, ValidationStatus, float, str]:
        claim_lower = claim.lower()
        best_source = "No matching source"
        best_score = 0

        for source in source_pool:
            overlap = len(set(claim_lower.split()) & set(source.lower().split()))
            if overlap > best_score:
                best_score = overlap
                best_source = source

        if best_score >= 4:
            return best_source, "supported", min(1.0, agent_confidence + 0.05), "Strong lexical alignment with retrieved evidence."
        if best_score >= 2:
            return best_source, "weakly_supported", agent_confidence, "Partial alignment with retrieved evidence."
        return best_source, "unsupported", max(0.1, agent_confidence - 0.2), "No strong evidence match was found."

    def _synthesize(
        self,
        task: Task,
        agent_outputs: List[AgentResponse],
        critiques: List[Critique],
        validations: List[ValidationResult],
    ) -> DecisionReport:
        supported_claims = [validation.claim for validation in validations if validation.status == "supported"]
        weakly_supported_claims = [validation.claim for validation in validations if validation.status == "weakly_supported"]
        unsupported_claims = [validation.claim for validation in validations if validation.status == "unsupported"]
        dissenting_views = [f"{response.agent_name}: {response.stance}" for response in agent_outputs if response.confidence < 0.8 or response.risks]

        top_agent = max(agent_outputs, key=lambda response: response.confidence)
        average_agent_confidence = sum(response.confidence for response in agent_outputs) / max(1, len(agent_outputs))
        total_claims = max(1, len(validations))
        evidence_score = (len(supported_claims) + 0.5 * len(weakly_supported_claims)) / total_claims
        critique_penalty = 0.02 * len(critiques)
        unsupported_penalty = 0.03 * (len(unsupported_claims) / total_claims)
        raw_confidence = (0.55 * average_agent_confidence) + (0.25 * evidence_score) + (0.2 * top_agent.confidence)
        confidence_score = round(max(0.0, min(1.0, raw_confidence - critique_penalty - unsupported_penalty)), 2)

        recommendation = self._recommendation_from_domain(task.domain, agent_outputs)
        risks = self._merge_unique([risk for response in agent_outputs for risk in response.risks] + [critique.objection for critique in critiques])

        return DecisionReport(
            query_id=task.query_id,
            recommendation=recommendation,
            confidence_score=confidence_score,
            supporting_claims=supported_claims[:5],
            dissenting_views=dissenting_views[:5],
            risks=risks[:5],
            tradeoffs=["Speed versus scrutiny", "Consensus versus visible dissent", "Accuracy versus completeness"],
            what_would_change_the_decision=[
                "Strong evidence that reverses the highest-risk claim",
                "A new stakeholder constraint",
                "A materially different domain context",
            ],
            agent_outputs=agent_outputs,
            critiques=critiques,
            validations=validations,
        )

    def _recommendation_from_domain(self, domain: Domain, agent_outputs: List[AgentResponse]) -> str:
        if domain == "policy":
            return "Use a staged, auditable rollout with explicit governance checks."
        if domain == "healthcare":
            return "Prefer the safest evidence-backed option and require human review."
        if domain == "security":
            return "Adopt the more conservative option and validate assumptions before deployment."
        if domain == "business":
            return "Choose the option with the best long-run execution and risk-adjusted value."
        if domain == "research":
            return "Keep the conclusion provisional until adversarial evidence is resolved."

        strongest = max(agent_outputs, key=lambda response: response.confidence)
        return strongest.stance

    def _merge_unique(self, values: Iterable[str]) -> List[str]:
        merged: List[str] = []
        for value in values:
            if value not in merged:
                merged.append(value)
        return merged