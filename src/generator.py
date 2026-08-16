"""
src/generator.py

LLM Generator Engine using Gemma 4 32b (models/gemma-4-31b-it) via Google Gemini API.
Calls the LLM with scoped section system instructions and user evidence prompts.
Includes response cleaning to strip LLM reasoning/drafting preambles, resilient exponential backoff retry logic,
and rate-controlled asynchronous execution capabilities.
"""

import os
import json
import re
import time
import asyncio
import urllib.request
import urllib.error
from typing import List, Tuple, Dict


class LLMGenerator:
    """
    Interface to Google Gemini API targeting Gemma 4 32b (models/gemma-4-31b-it).
    Includes automatic exponential backoff retries and parallel async execution.
    """

    def __init__(self, api_key: str = None, model: str = "gemma-4-31b-it"):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY", "")
        if not self.api_key:
            try:
                import streamlit as st
                self.api_key = st.secrets.get("GEMINI_API_KEY", "")
            except Exception:
                pass
        self.model = model
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"

    def _clean_llm_response(self, text: str) -> str:
        """
        Strips scratchpad, drafting notes, prompt reflections, and bullet lists,
        returning clean regulatory prose paragraphs.
        """
        refined_match = re.findall(r'Refining for Regulatory Tone:\s*["“](.*?)["”]', text, re.DOTALL | re.IGNORECASE)
        if refined_match:
            return "\n\n".join(refined_match).strip()

        drafted_quotes = re.findall(r'Drafting.*?:?\s*["“](.*?)["”]', text, re.DOTALL | re.IGNORECASE)
        if len(drafted_quotes) >= 2:
            return " ".join(drafted_quotes).strip()

        blocks = [b.strip() for b in text.split('\n\n') if b.strip()]
        clean_blocks = []

        for block in blocks:
            lines = [l.strip() for l in block.split('\n') if l.strip()]
            is_scratchpad = any(
                l.startswith(('*', '-', '•', '1.', '2.', '3.', '4.', '5.')) or
                re.match(r'^(?:Role|Task|Section|Evidence Packet|Constraints|Instructions|Draft|Drafting|Check|Introduction|PT Analysis|Outcome Analysis|Action Statement|Grounding Rule|Tone & Style|No Unsupported|History of Actions|Format|No boilerplate):', l, re.IGNORECASE)
                for l in lines
            )
            if not is_scratchpad:
                prose_lines = [l for l in lines if not l.startswith(('*', '-', '•'))]
                if prose_lines:
                    clean_blocks.append(" ".join(prose_lines))

        cleaned = "\n\n".join(clean_blocks).strip()

        if cleaned.startswith('"') and cleaned.endswith('"'):
            cleaned = cleaned[1:-1].strip()

        return cleaned if cleaned else text.strip()

    def generate_section_text(self, system_instruction: str, user_prompt: str, retries: int = 5) -> str:
        """
        Synchronous API call with exponential backoff retries targeting Gemma 4 32b.
        """
        url = f"{self.base_url}?key={self.api_key}"
        
        full_prompt = (
            f"{system_instruction}\n\n"
            f"CRITICAL FORMATTING INSTRUCTION: Write ONLY plain paragraph text. Do NOT write any bullet points (*), lists, or scratchpad notes.\n\n"
            f"{user_prompt}"
        )

        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": full_prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.1,
                "topP": 0.95,
                "maxOutputTokens": 2048
            }
        }

        for attempt in range(1, retries + 1):
            try:
                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"}
                )
                with urllib.request.urlopen(req, timeout=35) as resp:
                    res_data = json.loads(resp.read().decode("utf-8"))
                    candidates = res_data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            raw_text = parts[0].get("text", "").strip()
                            return self._clean_llm_response(raw_text)
                    raise ValueError("LLM returned empty candidate text.")

            except Exception as e:
                sleep_sec = attempt * 3
                print(f"    [Attempt {attempt}/{retries} for {self.model} failed: {type(e).__name__}] Retrying in {sleep_sec}s...")
                time.sleep(sleep_sec)

        raise RuntimeError(f"LLM Generation failed for {self.model} after {retries} retries.")

    async def generate_sections_parallel(self, section_requests: List[Tuple[str, str, str]], max_concurrency: int = 1) -> Dict[str, str]:
        """
        Generates multiple report sections with controlled pacing to respect API rate limits.
        """
        semaphore = asyncio.Semaphore(max_concurrency)

        async def _worker(sec_id: str, sys_inst: str, user_prompt: str) -> Tuple[str, str]:
            async with semaphore:
                res_text = await asyncio.to_thread(self.generate_section_text, sys_inst, user_prompt)
                await asyncio.sleep(1.0)
                return sec_id, res_text

        tasks = [
            _worker(sec_id, sys_inst, user_prompt)
            for sec_id, sys_inst, user_prompt in section_requests
        ]
        results = await asyncio.gather(*tasks)
        return {sec_id: text for sec_id, text in results}


if __name__ == "__main__":
    gen = LLMGenerator()
    out = gen.generate_section_text(
        "You are a regulatory writer.",
        "Summarize: Total cases 1024, serious cases 1023 (99.9%)."
    )
    print("Test output:", out[:100])
