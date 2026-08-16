"""
src/analyzer.py

Deterministic Analytics Engine for PADER ICSR Dataset.
Computes all numerical counts, distributions, age buckets, rankings, and time trends.
Zero LLM involvement -- 100% deterministic Pandas/Python calculations.
"""

import os
import math
import pandas as pd
from collections import Counter


class ICSRAnalyzer:
    """
    Analyzes an ICSR dataset (Excel or CSV) and produces a structured,
    deterministic evidence dictionary for report generation.
    """

    def __init__(self, file_path: str):
        self.file_path = file_path
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Dataset not found at {file_path}")
        
        if file_path.endswith('.xlsx') or file_path.endswith('.xls'):
            self.raw_df = pd.read_excel(file_path)
        else:
            self.raw_df = pd.read_csv(file_path)
        
        # Preprocess and create case-level deduplicated dataframe
        self.case_df = self.raw_df.drop_duplicates(subset=['safetyreportid']).copy()

    def get_summary_metrics(self) -> dict:
        """
        Compute total cases, serious vs non-serious, and date ranges.
        """
        total_rows = len(self.raw_df)
        total_cases = int(self.case_df['safetyreportid'].nunique())
        
        # Serious cases (case-level)
        serious_series = self.case_df['serious'].astype(str).str.lower().str.strip()
        serious_cases = int((serious_series == 'serious').sum())
        non_serious_cases = total_cases - serious_cases
        serious_pct = round((serious_cases / total_cases) * 100, 2) if total_cases > 0 else 0.0

        # Date range parsing
        rec_dates = pd.to_datetime(self.case_df['receivedate'].astype(str), format='%Y%m%d', errors='coerce')
        min_date = rec_dates.min().strftime('%Y-%m-%d') if pd.notna(rec_dates.min()) else "N/A"
        max_date = rec_dates.max().strftime('%Y-%m-%d') if pd.notna(rec_dates.max()) else "N/A"

        return {
            "total_rows": total_rows,
            "total_cases": total_cases,
            "serious_cases": serious_cases,
            "non_serious_cases": non_serious_cases,
            "serious_percentage": serious_pct,
            "reporting_period_start": min_date,
            "reporting_period_end": max_date
        }

    def get_demographics(self) -> dict:
        """
        Compute age group, sex, and country breakdowns.
        """
        total_cases = len(self.case_df)

        # Age Group Bucketing
        def bucket_age(age):
            if pd.isna(age):
                return 'Unknown'
            try:
                age_val = float(age)
                if age_val < 18:
                    return 'Pediatric (<18)'
                elif age_val < 65:
                    return 'Adult (18-64)'
                else:
                    return 'Elderly (65+)'
            except (ValueError, TypeError):
                return 'Unknown'

        self.case_df['age_bucket'] = self.case_df['patient_patientonsetage'].apply(bucket_age)
        age_counts = self.case_df['age_bucket'].value_counts().to_dict()
        age_breakdown = {}
        for group, count in age_counts.items():
            pct = round((count / total_cases) * 100, 2)
            age_breakdown[group] = {"count": int(count), "percentage": pct}

        # Sex Breakdown
        sex_series = self.case_df['patient_patientsex'].astype(str).str.lower().str.strip()
        sex_counts = sex_series.value_counts(dropna=False).to_dict()
        sex_breakdown = {}
        for sex, count in sex_counts.items():
            label = 'Female' if sex == 'female' else ('Male' if sex == 'male' else 'Unknown')
            pct = round((count / total_cases) * 100, 2)
            sex_breakdown[label] = sex_breakdown.get(label, {"count": 0, "percentage": 0.0})
            sex_breakdown[label]["count"] += int(count)
            sex_breakdown[label]["percentage"] = round((sex_breakdown[label]["count"] / total_cases) * 100, 2)

        # Country Breakdown
        country_counts = self.case_df['occurcountry'].astype(str).str.upper().value_counts().head(10).to_dict()
        country_breakdown = {}
        for country, count in country_counts.items():
            pct = round((count / total_cases) * 100, 2)
            country_breakdown[country] = {"count": int(count), "percentage": pct}

        return {
            "age_breakdown": age_breakdown,
            "sex_breakdown": sex_breakdown,
            "country_breakdown": country_breakdown
        }

    def get_reaction_analysis(self) -> dict:
        """
        Compute top MedDRA PT reactions and outcome distributions.
        """
        total_cases = len(self.case_df)

        # Unique cases per reaction PT
        pt_case_counts = self.raw_df.groupby('patient_reaction_reactionmeddrapt')['safetyreportid'].nunique().sort_values(ascending=False)
        top_reactions = []
        for pt, count in pt_case_counts.head(15).items():
            top_reactions.append({
                "reaction_pt": str(pt),
                "case_count": int(count),
                "percentage_of_total_cases": round((count / total_cases) * 100, 2)
            })

        # Outcomes (parsed from comma-separated list of values)
        outcomes_list = []
        for val in self.raw_df['patient_reaction_reactionoutcome'].dropna():
            parts = [p.strip().lower() for p in str(val).split(',')]
            outcomes_list.extend(parts)
        
        outcome_counter = Counter(outcomes_list)
        total_outcomes = sum(outcome_counter.values())
        outcome_breakdown = {}
        for outcome, count in outcome_counter.most_common():
            outcome_breakdown[outcome] = {
                "count": count,
                "percentage": round((count / total_outcomes) * 100, 2) if total_outcomes > 0 else 0.0
            }

        return {
            "top_reactions": top_reactions,
            "outcome_breakdown": outcome_breakdown
        }

    def get_serious_and_expedited_metrics(self) -> dict:
        """
        Compute 15-day alert / expedited case counts and criteria flags.
        """
        total_cases = len(self.case_df)
        
        # 15-day alert / expedite flags
        expedite_series = self.case_df['fulfillexpeditecriteria'].astype(str).str.lower().str.strip()
        expedited_cases = int((expedite_series == 'yes').sum())
        expedited_pct = round((expedited_cases / total_cases) * 100, 2)

        # Seriousness criteria flags
        ser_cols = {
            "seriousnesshospitalization": "Hospitalization / Prolonged Hospitalization",
            "seriousnessdeath": "Death",
            "seriousnesslifethreatening": "Life-Threatening",
            "seriousnessdisabling": "Disabling / Incapacitating",
            "seriousnesscongenitalanomali": "Congenital Anomaly",
            "seriousnessother": "Other Medically Important Condition"
        }

        criteria_counts = {}
        for col, label in ser_cols.items():
            if col in self.case_df.columns:
                col_series = self.case_df[col].astype(str).str.lower().str.strip()
                count = int((col_series == 'yes').sum())
                pct = round((count / total_cases) * 100, 2)
                criteria_counts[label] = {"count": count, "percentage": pct}

        return {
            "expedited_cases": expedited_cases,
            "expedited_percentage": expedited_pct,
            "seriousness_criteria_counts": criteria_counts
        }

    def get_trends(self) -> dict:
        """
        Compute monthly trends over the reporting period.
        """
        rec_dates = pd.to_datetime(self.case_df['receivedate'].astype(str), format='%Y%m%d', errors='coerce')
        monthly_series = rec_dates.dt.to_period('M').value_counts().sort_index()
        
        monthly_trends = []
        for period, count in monthly_series.items():
            monthly_trends.append({
                "month": str(period),
                "case_count": int(count)
            })

        return {
            "monthly_trends": monthly_trends
        }

    def get_case_index_sample(self, limit: int = 50) -> list:
        """
        Extract a structured case listing sample for the appendix.
        """
        sample_rows = []
        for idx, row in self.case_df.head(limit).iterrows():
            rec_date_str = str(row.get('receivedate', ''))
            formatted_date = f"{rec_date_str[:4]}-{rec_date_str[4:6]}-{rec_date_str[6:8]}" if len(rec_date_str) == 8 else rec_date_str
            
            sample_rows.append({
                "safetyreportid": str(row.get('safetyreportid', '')),
                "country": str(row.get('occurcountry', '')).upper(),
                "age": str(row.get('patient_patientonsetage', 'N/A')),
                "sex": str(row.get('patient_patientsex', 'Unknown')).capitalize(),
                "reaction_pt": str(row.get('patient_reaction_reactionmeddrapt', '')),
                "seriousness": str(row.get('serious', '')).capitalize(),
                "reporting_date": formatted_date,
                "outcome": str(row.get('patient_reaction_reactionoutcome', 'Unknown'))
            })
        return sample_rows

    def analyze_all(self) -> dict:
        """
        Runs all analyses and aggregates into a single evidence dictionary.
        """
        return {
            "summary": self.get_summary_metrics(),
            "demographics": self.get_demographics(),
            "reactions": self.get_reaction_analysis(),
            "serious_expedited": self.get_serious_and_expedited_metrics(),
            "trends": self.get_trends(),
            "case_sample": self.get_case_index_sample(limit=30)
        }


if __name__ == "__main__":
    analyzer = ICSRAnalyzer("/home/rahul/development_walkins/challenge from company/Bisoprolol_icsr_sample_1068rows.xlsx")
    res = analyzer.analyze_all()
    print("Summary:", res["summary"])
    print("Demographics:", res["demographics"]["age_breakdown"])
