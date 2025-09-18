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
{self.prompt_template.format(analysis_points=analysis_str)}

Input data to analyze:
{input_data}

Please provide your analysis in the following JSON format:
{{
    "agent_type": "{self.name}",
    "analysis_results": {{
        {self._generate_json_structure(analysis_points)}
    }},
    "confidence_score": <float between 0 and 1>,
    "summary": "<brief summary of findings>"
}}
"""
        return prompt

    def _generate_json_structure(self, analysis_points: List[str]) -> str:
        json_fields = []
        for point in analysis_points:
            field_name = point.lower().replace(" ", "_").replace("-", "_")
            json_fields.append(f'        "{field_name}": "<your analysis for {point}>"')
        return ",\n".join(json_fields)

    def extract_key_findings(self, response: str) -> Dict[str, Any]:
        try:
            response = response.strip()
            if response.startswith('```json'):
                response = response[7:]
            if response.endswith('```'):
                response = response[:-3]
            response = response.strip()

            parsed = json.loads(response)

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