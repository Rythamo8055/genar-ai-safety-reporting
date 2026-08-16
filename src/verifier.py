"""
src/verifier.py

Enterprise Grounding Verification and Semantic Entity-Metric Assertion Engine.
Audits generated report narratives against deterministic evidence to detect numerical
hallucinations, metric swaps (e.g. swapping serious vs non-serious counts), and ungrounded figures.
"""

import re
from typing import Dict, Any, List


class GroundingVerifier:
    """
    Bulletproof Verification Engine combining Numerical Set Assertion
    and Semantic Metric-Tuple Association Validation.
    """

    def __init__(self, evidence_data: Dict[str, Any]):
        self.evidence = evidence_data
        self.allowed_numbers = self._extract_all_numbers(evidence_data)
        
        # Dynamically extract reporting period years from evidence
        start_year = self.evidence["summary"].get("reporting_period_start", "")[:4]
        end_year = self.evidence["summary"].get("reporting_period_end", "")[:4]
        if start_year.isdigit():
            self.allowed_numbers.add(int(start_year))
        if end_year.isdigit():
            self.allowed_numbers.add(int(end_year))

        # Domain constants (age cohort thresholds, regulatory CFR numbers, 15-day alert period)
        self.allowed_numbers.update({18, 65, 21, 314, 80, 15, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10})

        # Key metric reference bindings for tuple assertion
        self.key_metric_bindings = {
            "total_cases": self.evidence["summary"]["total_cases"],
            "serious_cases": self.evidence["summary"]["serious_cases"],
            "non_serious_cases": self.evidence["summary"]["non_serious_cases"],
            "serious_percentage": self.evidence["summary"]["serious_percentage"],
            "expedited_cases": self.evidence["serious_expedited"]["expedited_cases"],
            "expedited_percentage": self.evidence["serious_expedited"]["expedited_percentage"],
        }

    def _extract_all_numbers(self, data: Any) -> set:
        """
        Recursively extracts all numeric values (integers, floats, percentages) from evidence dict.
        """
        numbers = set()
        if isinstance(data, dict):
            for v in data.values():
                numbers.update(self._extract_all_numbers(v))
        elif isinstance(data, list):
            for item in data:
                numbers.update(self._extract_all_numbers(item))
        elif isinstance(data, (int, float)):
            val = round(float(data), 2)
            numbers.add(val)
            if val.is_integer():
                numbers.add(int(val))
        elif isinstance(data, str):
            clean_str = re.sub(r'(\d+),(\d+)', r'\1\2', data)
            found = re.findall(r'\b\d+(?:\.\d+)?\b', clean_str)
            for f in found:
                try:
                    val = float(f)
                    numbers.add(round(val, 2))
                    if val.is_integer():
                        numbers.add(int(val))
                except ValueError:
                    pass
        return numbers

    def audit_semantic_tuples(self, text: str) -> List[str]:
        """
        Checks for high-risk metric swaps (e.g. attributing '1023' to 'non-serious' or '1' to 'serious').
        Returns list of semantic violation flags.
        """
        violations = []
        clean = re.sub(r'(\d+),(\d+)', r'\1\2', text.lower())

        # Check Serious vs Non-Serious metric swaps
        serious_match = re.search(r'serious\s*(?:cases|reports)?\s*(?:were|of|totaling)?\s*(\d+)', clean)
        non_serious_match = re.search(r'non-serious\s*(?:cases|reports)?\s*(?:were|of|totaling)?\s*(\d+)', clean)

        if serious_match:
            val = int(serious_match.group(1))
            if val == self.evidence["summary"]["non_serious_cases"] and val != self.evidence["summary"]["serious_cases"]:
                violations.append(f"Metric Swap Detected: Serious cases reported as {val} (expected {self.evidence['summary']['serious_cases']})")

        if non_serious_match:
            val = int(non_serious_match.group(1))
            if val == self.evidence["summary"]["serious_cases"] and val != self.evidence["summary"]["non_serious_cases"]:
                violations.append(f"Metric Swap Detected: Non-serious cases reported as {val} (expected {self.evidence['summary']['non_serious_cases']})")

        return violations

    def audit_section(self, section_name: str, generated_text: str) -> Dict[str, Any]:
        """
        Audits a generated text section using Numerical Set Assertion AND Semantic Tuple Validation.
        """
        clean_text = re.sub(r'(\d+),(\d+)', r'\1\2', generated_text)
        found_numbers = re.findall(r'\b\d+(?:\.\d+)?\b', clean_text)
        
        grounded_count = 0
        unverified_numbers = []
        
        for num_str in found_numbers:
            try:
                num = float(num_str)
                num_rounded = round(num, 2)
                num_int = int(num) if num.is_integer() else None

                if (num_rounded in self.allowed_numbers) or \
                   (num_int is not None and num_int in self.allowed_numbers):
                    grounded_count += 1
                else:
                    unverified_numbers.append(num_str)
            except ValueError:
                pass

        total_extracted = len(found_numbers)
        verification_rate = round((grounded_count / total_extracted) * 100, 2) if total_extracted > 0 else 100.0
        
        # Audit semantic tuple relationships
        semantic_violations = self.audit_semantic_tuples(generated_text)
        
        is_passed = (len(unverified_numbers) == 0 or verification_rate >= 90.0) and len(semantic_violations) == 0

        return {
            "section_name": section_name,
            "total_numbers_found": total_extracted,
            "grounded_count": grounded_count,
            "verification_rate": verification_rate,
            "unverified_numbers": list(set(unverified_numbers)),
            "semantic_violations": semantic_violations,
            "passed": is_passed
        }


if __name__ == "__main__":
    from src.analyzer import ICSRAnalyzer
    analyzer = ICSRAnalyzer("/home/rahul/development_walkins/challenge from company/Bisoprolol_icsr_sample_1068rows.xlsx")
    evidence = analyzer.analyze_all()
    verifier = GroundingVerifier(evidence)
    res = verifier.audit_section("Test", "There were 1023 serious cases and 1 non-serious case.")
    print("Audit Result:", res)
