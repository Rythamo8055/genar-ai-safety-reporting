"""
src/models.py

Data structures and types for the Regulatory Safety Report Generation Platform.
Defines strongly typed schemas for evidence packets, section specifications, audit logs,
and LLM evaluation scores.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional


@dataclass
class SummaryMetrics:
    total_rows: int
    total_cases: int
    serious_cases: int
    non_serious_cases: int
    serious_percentage: float
    reporting_period_start: str
    reporting_period_end: str


@dataclass
class SectionSpec:
    section_id: str
    title: str
    required_metrics: List[str]
    prompt_key: str
    description: str


@dataclass
class ReportSpec:
    report_type: str
    report_title: str
    regulatory_framework: str
    sections: List[SectionSpec]


@dataclass
class AuditResult:
    section_name: str
    total_numbers_found: int
    grounded_count: int
    verification_rate: float
    unverified_numbers: List[str]
    passed: bool


@dataclass
class EvaluationScore:
    section_id: str
    grounding_score: float  # 1.0 - 5.0
    regulatory_tone_score: float  # 1.0 - 5.0
    completeness_score: float  # 1.0 - 5.0
    safety_guardrail_passed: bool
    feedback: str
