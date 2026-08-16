"""
prompts/prompts.py

Section-specific system instructions and prompt templates for regulatory PADER report generation.
Keeps LLM context minimal, scoped, and strictly grounded in deterministic data.
"""

SYSTEM_INSTRUCTION = """You are an expert Regulatory Affairs Safety Specialist assisting in authoring a Postmarketing Adverse Drug Experience Report (PADER) for Bisoprolol.

STRICT REGULATORY COMPLIANCE RULES:
1. Grounding Rule: You MUST strictly summarize ONLY the exact figures, percentages, and metrics provided in the Section Evidence Packet. Do NOT invent, extrapolate, or hallucinate numbers or clinical facts.
2. Tone & Style: Maintain an objective, neutral, precise, and formal regulatory tone suitable for health authorities (FDA / EMA).
3. No Unsupported Safety Inferences: Do NOT declare a product "safe" or "unsafe" beyond what the quantitative evidence packet explicitly supports.
4. History of Actions Rule: If the dataset contains no reported actions, explicitly state that no safety-related actions were supplied for this reporting period.
5. Format: Output clean, well-formatted Markdown text without boilerplate introduction or wrapping code blocks.
6. Absolute Zero Scratchpad Rule: Write ONLY the final regulatory narrative paragraphs. Do NOT write any bullet points (*), scratchpad notes, drafting steps, or role-playing reflections.
"""

SECTION_PROMPTS = {
    "reporting_period": """
SECTION: 1. Reporting Period & Product Profile

EVIDENCE PACKET:
- Product Name: Bisoprolol (Beta-adrenergic blocking agent)
- Reporting Period Start: {summary[reporting_period_start]}
- Reporting Period End: {summary[reporting_period_end]}
- Total ICSR Rows: {summary[total_rows]}
- Unique Safety Report IDs (Total Cases): {summary[total_cases]}

INSTRUCTIONS:
Write a brief, precise regulatory introductory section stating the drug product name, therapeutic class, the exact 1-year reporting period covered, the total ICSR records processed, and the count of unique patient cases (1,024). Output ONLY clean paragraph text.
""",

    "narrative_summary": """
SECTION: 2. Executive Narrative Summary and Analysis

EVIDENCE PACKET:
- Total Unique Cases: {summary[total_cases]}
- Serious Cases: {summary[serious_cases]} ({summary[serious_percentage]}%)
- Non-Serious Cases: {summary[non_serious_cases]}
- Primary Age Group: {demographics[age_breakdown][Elderly (65+)][count]} cases ({demographics[age_breakdown][Elderly (65+)][percentage]}%) in Elderly (65+)
- Top Reported Adverse Event: {reactions[top_reactions][0][reaction_pt]} ({reactions[top_reactions][0][case_count]} cases, {reactions[top_reactions][0][percentage_of_total_cases]}%)
- 15-Day Expedited Alert Cases: {serious_expedited[expedited_cases]} ({serious_expedited[expedited_percentage]}%)

INSTRUCTIONS:
Write an executive narrative summary providing a high-level overview of the ICSR dataset. State the overall case volume, the proportion of serious vs. non-serious reports, the predominant demographic cohort (Elderly), and the most frequent adverse event. Maintain a factual, neutral regulatory tone. Output ONLY clean paragraph text.
""",

    "summary_cases": """
SECTION: 3. Summary Analysis of Cases (Demographics & Geography)

EVIDENCE PACKET:
Demographic & Geographic Distribution:
- Total Unique Cases: {summary[total_cases]}
- Age Group Breakdown:
  * Elderly (65+): {demographics[age_breakdown][Elderly (65+)][count]} cases ({demographics[age_breakdown][Elderly (65+)][percentage]}%)
  * Adult (18-64): {demographics[age_breakdown][Adult (18-64)][count]} cases ({demographics[age_breakdown][Adult (18-64)][percentage]}%)
  * Pediatric (<18): {demographics[age_breakdown][Pediatric (<18)][count]} cases ({demographics[age_breakdown][Pediatric (<18)][percentage]}%)
  * Unknown Age: {demographics[age_breakdown][Unknown][count]} cases ({demographics[age_breakdown][Unknown][percentage]}%)
- Sex Breakdown:
  * Female: {demographics[sex_breakdown][Female][count]} cases ({demographics[sex_breakdown][Female][percentage]}%)
  * Male: {demographics[sex_breakdown][Male][count]} cases ({demographics[sex_breakdown][Male][percentage]}%)
  * Unknown: {demographics[sex_breakdown][Unknown][count]} cases ({demographics[sex_breakdown][Unknown][percentage]}%)
- Top Primary Occurrence Countries:
  * EU (regional code): {demographics[country_breakdown][EU][count]} cases ({demographics[country_breakdown][EU][percentage]}%)
  * United Kingdom: {demographics[country_breakdown][UNITED KINGDOM][count]} cases ({demographics[country_breakdown][UNITED KINGDOM][percentage]}%)
  * France: {demographics[country_breakdown][FRANCE][count]} cases ({demographics[country_breakdown][FRANCE][percentage]}%)
  * Canada: {demographics[country_breakdown][CANADA][count]} cases ({demographics[country_breakdown][CANADA][percentage]}%)
  * Italy: {demographics[country_breakdown][ITALY][count]} cases ({demographics[country_breakdown][ITALY][percentage]}%)

INSTRUCTIONS:
Provide a structured analytical narrative summarizing case distribution across age groups, sex, and reporting countries. Highlight that the patient population is predominantly elderly, with balanced gender distribution and primary reporting from EU and UK regions. Output ONLY clean paragraph text.
""",

    "reaction_analysis": """
SECTION: 4. Adverse Reaction / Event Analysis

EVIDENCE PACKET:
Top MedDRA Preferred Terms (PTs) by Unique Case Count:
{reactions_formatted}

Reaction Outcomes Distribution across reported events:
{outcomes_formatted}

INSTRUCTIONS:
Provide a detailed narrative analyzing the most common MedDRA Preferred Terms (PTs) reported during the monitoring period. Discuss the leading reaction (Acute kidney injury) followed by Drug ineffective, Hypokalaemia, Hyponatraemia, and Cholestasis. Detail the distribution of reaction outcomes (Recovered/Resolved, Unknown, Ongoing, Recovering, Fatal, Sequelae) clearly citing the exact figures. Output ONLY clean paragraph text.
""",

    "serious_cases": """
SECTION: 5. Serious Cases and 15-Day Expedited Alerts

EVIDENCE PACKET:
- Total Expedited 15-Day Alert Cases: {serious_expedited[expedited_cases]} ({serious_expedited[expedited_percentage]}% of all cases)
- Seriousness Criteria Breakdown (Non-mutually exclusive):
{seriousness_criteria_formatted}

INSTRUCTIONS:
Write a regulatory evaluation of serious cases and 15-day expedited alerts (`fulfillexpeditecriteria`). Explain that 1,023 of 1,024 cases (99.9%) were submitted under expedited reporting criteria. Detail the distribution across seriousness criteria (Hospitalization, Death, Life-Threatening, Disabling, Congenital Anomaly, and Other Medically Important Conditions). Output ONLY clean paragraph text.
""",

    "trends_observations": """
SECTION: 6. Trends and Important Observations

EVIDENCE PACKET:
- Reporting Period: {summary[reporting_period_start]} to {summary[reporting_period_end]}
- Monthly Case Distribution:
{monthly_trends_formatted}
- Clinical Cohort Observation: Predominance of Elderly patients (65+ years) accounting for {demographics[age_breakdown][Elderly (65+)][count]} cases ({demographics[age_breakdown][Elderly (65+)][percentage]}%).

INSTRUCTIONS:
Provide a temporal trend analysis describing monthly case reception patterns over the 12-month period. Discuss monthly fluctuations (highlighting peak months July and October 2025) and contextualize demographic observations. Output ONLY clean paragraph text.
""",

    "history_of_actions": """
SECTION: 7. History of Safety-Related Actions

EVIDENCE PACKET:
Action Data Provided: None (Dataset Condition)

INSTRUCTIONS:
Explicitly state that no safety-related regulatory actions, labeling modifications, or risk-minimization measures were supplied or recorded in the dataset for this reporting period. Output ONLY clean paragraph text.
"""
}
