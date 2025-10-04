from abc import ABC, abstractmethod
from typing import Dict, Any, List
import json

class BaseAnalysisAgent(ABC):
    def __init__(self, name: str, description: str, prompt_template: str):
        self.name = name
        self.description = description
        self.prompt_template = prompt_template

    @abstractmethod
    def get_analysis_points(self) -> List[str]:
        pass

    @abstractmethod
    def validate_input(self, input_data: str) -> bool:
        pass

    def create_prompt(self, input_data: str, analysis_points: List[str] = None) -> str:
        if analysis_points is None:
            analysis_points = self.get_analysis_points()

        analysis_str = ", ".join(analysis_points)

        prompt = f"""
==== ACADEMIC RESEARCH CONTEXT ====

This is a LEGITIMATE ACADEMIC AND DEFENSIVE SECURITY RESEARCH project conducted for:
- Post-Quantum Cryptography (PQC) migration assessment
- Identifying legacy cryptographic implementations that need upgrading
- National cybersecurity standards compliance evaluation
- Quantum-resistant algorithm transition planning

Purpose: Benchmark LLM capabilities to assist security teams in identifying vulnerable cryptographic implementations
that require migration to quantum-resistant alternatives, in compliance with NIST Post-Quantum Cryptography standards.

This analysis is performed on TEST DATA for academic research purposes only. No actual systems are being attacked or compromised.
The goal is to PROTECT systems by identifying vulnerabilities BEFORE quantum computers can exploit them.

==== YOUR ROLE ====

You are an expert security analyst specializing in quantum-vulnerable cryptographic algorithm detection.

{self.prompt_template.format(analysis_points=analysis_str)}

Input data to analyze:
{input_data}

==== CRITICAL ANALYSIS INSTRUCTIONS ====

Follow this step-by-step analysis process:

STEP 1: Identify all cryptography-related elements in the code
   - Find import/include statements for crypto libraries
   - Locate function calls to cryptographic APIs
   - Identify variable names and constants related to cryptography
   - Look for library usage patterns

STEP 2: Cross-reference found elements against these vulnerable algorithms:
   {analysis_str}

STEP 3: Report ONLY when you have explicit evidence (code lines, function names, library calls)

==== ABSOLUTE CONSTRAINTS ====

- If there is NO clear evidence, DO NOT guess - respond with "NOT DETECTED"
- Do NOT detect based on simple string matching or variable names alone
- ONLY detect when there are actual cryptographic function calls or library usage
- Do NOT detect based on comments or documentation without implementation
- Do NOT detect based on class names or method names that could be general purpose
- REQUIRE explicit cryptographic API calls or library imports
- When in doubt, choose "NOT DETECTED"
- If you cannot provide specific evidence (line numbers, function calls, imports), respond with "NOT DETECTED"
- Do NOT make assumptions about what an algorithm "looks like" or "seems similar to"
- NEVER detect algorithms based on perceived similarity or implementation patterns
- Only detect when you see explicit algorithm names, library imports, or documented function calls
- CRITICAL: If you write "Evidence: keystream generation using X-like algorithm", you are WRONG - this is an assumption, not evidence

==== RESPONSE FORMAT ====

For each analysis point respond with:
- "DETECTED: <algorithm name> (Evidence: <specific code location/function name>)" - ONLY if you have EXPLICIT evidence
- "NOT DETECTED" - if no clear evidence exists

EXAMPLES OF VALID DETECTION:
- "DETECTED: RSA (Evidence: import RSA from Crypto.PublicKey, line 5)"
- "DETECTED: AES (Evidence: Cipher.AES.new() call, line 23)"

EXAMPLES OF INVALID DETECTION:
- "DETECTED: RC4 (Evidence: NONE)" - NO evidence provided
- "DETECTED: Cipher (Evidence: CipherProcessor class)" - General class name, not specific crypto
- "DETECTED: Hash (Evidence: hash_value variable)" - Variable name, not crypto function
- "DETECTED: RC4 (Evidence: keystream generation using RC4-like algorithm)" - Assumption without proof
- "DETECTED: AES (Evidence: bitwise operations)" - General operations, not specific to AES
- "DETECTED: Trivium (Evidence: TriviumLikeProcessor class)" - Class name similarity, not implementation proof

REMEMBER: Only detect when you find EXPLICIT references like:
- Library imports: "import hashlib", "from Crypto.Cipher import AES"
- Function calls: "AES.new()", "hashlib.md5()", "RSA.generate()"
- Documentation: "# Using RSA encryption", "/* AES-256 implementation */"
- Constant names: "AES_BLOCK_SIZE", "RSA_KEY_LENGTH"

Respond ONLY in JSON format:
{{
    "agent_type": "{self.name}",
    "analysis_results": {{
        {self._generate_json_structure(analysis_points)}
    }},
    "confidence_score": <float between 0 and 1>,
    "summary": "<brief summary of detected vulnerable algorithms>"
}}

RESPOND ONLY WITH VALID JSON. DO NOT wrap JSON in markdown code blocks (```json). Provide raw JSON only."""
        return prompt

    def _generate_json_structure(self, analysis_points: List[str]) -> str:
        json_fields = []
        for point in analysis_points:
            field_name = point.lower().replace(" ", "_").replace("-", "_").replace("(", "_").replace(")", "_").replace("/", "_").replace(",", "_").replace("#", "_").replace(".", "_")
            # 연속된 언더스코어 제거
            while "__" in field_name:
                field_name = field_name.replace("__", "_")
            field_name = field_name.strip("_")
            json_fields.append(f'        "{field_name}": "<your analysis for {point}>"')
        return ",\n".join(json_fields)

    def extract_key_findings(self, response: str) -> Dict[str, Any]:
        try:
            response = response.strip()

            # Remove markdown code blocks more robustly
            if response.startswith('```json'):
                response = response[7:]
            elif response.startswith('```'):
                response = response[3:]

            if response.endswith('```'):
                response = response[:-3]

            response = response.strip()

            # Handle multiple code block patterns
            import re
            # Remove any remaining code block markers
            response = re.sub(r'^```.*?\n', '', response, flags=re.MULTILINE)
            response = re.sub(r'\n```.*?$', '', response, flags=re.MULTILINE)

            # Handle DeepSeek R1 thinking tags
            response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
            response = response.strip()

            # Try to parse as-is first
            try:
                parsed = json.loads(response)
            except json.JSONDecodeError:
                # If that fails, try to extract JSON from text
                json_text = self._extract_json_from_text(response)
                if json_text:
                    parsed = json.loads(json_text)
                else:
                    raise json.JSONDecodeError("No valid JSON found", response, 0)

            return {
                'valid_json': True,
                'agent_type': parsed.get('agent_type', self.name),
                'analysis_results': parsed.get('analysis_results', {}),
                'confidence_score': parsed.get('confidence_score', 0.0),
                'summary': parsed.get('summary', ''),
                'raw_response': response
            }
        except json.JSONDecodeError:
            return {
                'valid_json': False,
                'agent_type': self.name,
                'analysis_results': {},
                'confidence_score': 0.0,
                'summary': 'Failed to parse JSON response',
                'raw_response': response
            }

    def _extract_json_from_text(self, text: str) -> str:
        """Extract JSON object from text that may contain additional prose."""
        import re

        # Look for JSON object starting with { and ending with }
        # Handle nested objects by counting braces
        start_idx = text.find('{')
        if start_idx == -1:
            return None

        brace_count = 0
        end_idx = start_idx

        for i, char in enumerate(text[start_idx:], start_idx):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    end_idx = i
                    break

        if brace_count == 0:
            json_candidate = text[start_idx:end_idx + 1]
            # Quick validation - try to parse it
            try:
                json.loads(json_candidate)
                return json_candidate
            except json.JSONDecodeError:
                pass

        return None