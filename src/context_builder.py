"""
src/context_builder.py

Context Engineering Module for Regulatory PADER Report Generation.
Assembles minimal, section-scoped Evidence Packets formatted as structured text.
Prevents LLM context clutter and data dumping.
"""

from prompts.prompts import SYSTEM_INSTRUCTION, SECTION_PROMPTS


class ContextBuilder:
    """
    Constructs section-specific prompt evidence packets from deterministic analytical results.
    """

    def __init__(self, evidence_data: dict):
        self.evidence = evidence_data

    def format_reactions_text(self) -> str:
        reactions = self.evidence["reactions"]["top_reactions"]
        lines = []
        for r in reactions[:10]:
            lines.append(f"  * {r['reaction_pt']}: {r['case_count']} cases ({r['percentage_of_total_cases']}% of total cases)")
        return "\n".join(lines)

    def format_outcomes_text(self) -> str:
        outcomes = self.evidence["reactions"].get("outcome_breakdown", self.evidence["reactions"].get("outcomes_breakdown", {}))
        lines = []
        for outcome, data in outcomes.items():
            lines.append(f"  * {outcome}: {data['count']} event reports ({data['percentage']}%)")
        return "\n".join(lines)

    def format_seriousness_criteria_text(self) -> str:
        criteria = self.evidence["serious_expedited"]["seriousness_criteria_counts"]
        lines = []
        for crit, data in criteria.items():
            lines.append(f"  * {crit}: {data['count']} cases ({data['percentage']}%)")
        return "\n".join(lines)

    def format_trends_text(self) -> str:
        trends = self.evidence["trends"]["monthly_trends"]
        lines = []
        for t in trends:
            lines.append(f"  * {t['month']}: {t['case_count']} cases")
        return "\n".join(lines)

    def build_section_prompt(self, section_key: str) -> tuple[str, str]:
        """
        Returns (system_instruction, user_prompt) for the specified section_key.
        """
        if section_key not in SECTION_PROMPTS:
            raise KeyError(f"Unknown section key: {section_key}")

        template = SECTION_PROMPTS[section_key]

        # Dynamic variable mapping
        kwargs = {
            "summary": self.evidence["summary"],
            "demographics": self.evidence["demographics"],
            "reactions": self.evidence["reactions"],
            "serious_expedited": self.evidence["serious_expedited"],
            "trends": self.evidence["trends"],
            "reactions_formatted": self.format_reactions_text(),
            "outcomes_formatted": self.format_outcomes_text(),
            "seriousness_criteria_formatted": self.format_seriousness_criteria_text(),
            "trends_formatted": self.format_trends_text(),
            "monthly_trends_formatted": self.format_trends_text()
        }

        user_prompt = template.format(**kwargs)
        return SYSTEM_INSTRUCTION, user_prompt


if __name__ == "__main__":
    from src.analyzer import ICSRAnalyzer
    analyzer = ICSRAnalyzer("/home/rahul/development_walkins/challenge from company/Bisoprolol_icsr_sample_1068rows.xlsx")
    evidence = analyzer.analyze_all()
    builder = ContextBuilder(evidence)
    sys_inst, user_prompt = builder.build_section_prompt("narrative_summary")
    print("User Prompt Sample:\n", user_prompt[:300])
