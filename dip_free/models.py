from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal


Domain = Literal["general", "policy", "healthcare", "business", "research", "security"]
AgentKind = Literal["research", "risk", "ethics", "policy", "economics", "strategy"]
ValidationStatus = Literal["supported", "weakly_supported", "unsupported"]


@dataclass
class Task:
    query_id: str
    query_text: str
    domain: Domain
    stakes: str
    constraints: List[str]
    required_agents: List[AgentKind]
    evidence_needed: List[str]
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResponse:
    agent_name: str
    stance: str
    claims: List[str]
    evidence: List[str]
    assumptions: List[str]
    confidence: float
    risks: List[str]
    open_questions: List[str]


@dataclass
class Critique:
    target_agent: str
    objection: str
    severity: Literal["low", "medium", "high"]
    evidence_against: List[str]
    unresolved_issue: str


@dataclass
class ValidationResult:
    claim_id: str
    claim: str
    status: ValidationStatus
    source: str
    confidence: float
    notes: str


@dataclass
class DecisionReport:
    query_id: str
    recommendation: str
    confidence_score: float
    supporting_claims: List[str]
    dissenting_views: List[str]
    risks: List[str]
    tradeoffs: List[str]
    what_would_change_the_decision: List[str]
    agent_outputs: List[AgentResponse]
    critiques: List[Critique]
    validations: List[ValidationResult]


ReportDict = Dict[str, Any]