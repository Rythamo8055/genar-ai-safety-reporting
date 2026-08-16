"""
src/human_review.py

Human Control and Review Gate for Regulatory Report Sign-off.
Provides programmatic and interactive review capabilities before final report publication.
"""


class HumanReviewGate:
    """
    Manages review status (APPROVED, FLAGGED, MODIFIED) for report sections.
    """

    def __init__(self):
        self.reviews = {}

    def add_section_for_review(self, section_id: str, title: str, text: str, verification_result: dict):
        """
        Registers a section for human control review.
        """
        auto_status = "APPROVED" if verification_result.get("passed", True) else "FLAGGED"
        self.reviews[section_id] = {
            "title": title,
            "text": text,
            "verification": verification_result,
            "status": auto_status,
            "reviewer_notes": f"Auto-verified ({verification_result.get('verification_rate', 100)}% grounded)" if auto_status == "APPROVED" else "Flagged for unverified figures."
        }

    def approve_section(self, section_id: str, reviewer_notes: str = "Approved by Regulatory Specialist"):
        """
        Explicitly approves a section.
        """
        if section_id in self.reviews:
            self.reviews[section_id]["status"] = "APPROVED"
            self.reviews[section_id]["reviewer_notes"] = reviewer_notes

    def flag_section(self, section_id: str, reviewer_notes: str):
        """
        Flags a section requiring revision.
        """
        if section_id in self.reviews:
            self.reviews[section_id]["status"] = "FLAGGED"
            self.reviews[section_id]["reviewer_notes"] = reviewer_notes

    def edit_section_text(self, section_id: str, new_text: str, reviewer_notes: str = "Manually edited during review"):
        """
        Updates text for a section based on human edit.
        """
        if section_id in self.reviews:
            self.reviews[section_id]["text"] = new_text
            self.reviews[section_id]["status"] = "MODIFIED"
            self.reviews[section_id]["reviewer_notes"] = reviewer_notes

    def get_review_summary(self) -> dict:
        """
        Returns an overall audit trail of human review.
        """
        total = len(self.reviews)
        approved = sum(1 for r in self.reviews.values() if r["status"] in ("APPROVED", "MODIFIED"))
        flagged = sum(1 for r in self.reviews.values() if r["status"] == "FLAGGED")

        return {
            "total_sections": total,
            "approved_sections": approved,
            "flagged_sections": flagged,
            "all_passed": flagged == 0
        }
