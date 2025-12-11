
import json
import os
import re
from typing import List, Dict, Any
import logging
import google.generativeai as genai

logger = logging.getLogger(__name__)


class RuleGenerator:
    def __init__(
        self,
        embedding_service,
        rag_service,
        store_keys: List[Dict[str, str]],
        model: str = "gemini-2.5-flash"  
    ):
        self.embedding_service = embedding_service
        self.rag_service = rag_service
        self.store_keys = store_keys
        self.model = model
        
        self.valid_keys = {key["value"]: key for key in store_keys}
        
        genai.configure(api_key=os.getenv("GEMINI_API_KEY")) # type: ignore
        
    async def generate(
        self,
        prompt: str,
        key_mappings: List[Dict[str, Any]],
        relevant_policies: List[str]
    ) -> Dict[str, Any]:
        
        logger.info(f"Generating rule for prompt: {prompt[:100]}...")
        
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(prompt, key_mappings, relevant_policies)
        
        try:
            gen_model = genai.GenerativeModel( #type: ignore
                model_name=self.model,
                system_instruction=system_prompt,
                generation_config={
                    "temperature": 0.1,
                    "response_mime_type": "application/json"
                }
            ) 
            
            response = await gen_model.generate_content_async(user_prompt)
            
            response_text = response.text
            logger.debug(f"LLM response: {response_text}")
            
        except Exception as e:
            logger.error(f"LLM call failed: {str(e)}")
            raise RuntimeError(f"Failed to generate rule: {str(e)}")
        
        result = self._parse_response(response_text) # type: ignore
        
        self._validate_rule(result["json_logic"])
        
        confidence = self._calculate_confidence(key_mappings, result["used_keys"])
        result["confidence_score"] = confidence
        
        result["key_mappings"] = [
            m for m in key_mappings 
            if m["mapped_to"] in result["used_keys"]
        ]
        
        return result
    
    def _build_system_prompt(self) -> str:
        keys_list = "\n".join([
            f"  - {key['value']} ({key['label']})"
            for key in self.store_keys
        ])
        
        return f"""You are a JSON Logic rule generator. Your job is to convert natural language descriptions into valid JSON Logic rules.

## JSON Logic Basics
JSON Logic uses operators like:
- {{"and": [conditions]}} - All conditions must be true
- {{"or": [conditions]}} - At least one condition must be true
- {{"if": [condition, then, else]}} - Conditional logic
- {{">": [{{\"var\": \"field\"}}, value]}} - Greater than comparison
- {{"<": [{{\"var\": \"field\"}}, value]}} - Less than comparison
- {{">=": [{{\"var\": \"field\"}}, value]}} - Greater than or equal
- {{"<=": [{{\"var\": \"field\"}}, value]}} - Less than or equal
- {{"==": [{{\"var\": \"field\"}}, value]}} - Equality check
- {{"!=": [{{\"var\": \"field\"}}, value]}} - Not equal
- {{"in": [value, {{\"var\": \"field\"}}]}} - Check if value is in array
- {{"!": condition}} - Logical NOT

## Available Fields (use these EXACTLY as "var" values)
{keys_list}

## Output Format
You MUST respond with a JSON object containing:
{{
  "json_logic": <the JSON Logic rule>,
  "explanation": "<1-3 sentence explanation of what the rule does>",
  "used_keys": ["<list of field keys used in the rule>"]
}}

## Important Rules
1. ONLY use field keys from the list above - never invent new fields
2. Always use {{"var": "field.name"}} syntax to reference fields
3. For "between" conditions, use nested "and" with >= and <=
4. For checking tags/arrays, use the "in" operator
5. Make sure the JSON Logic is syntactically valid
6. Be concise in your explanation - mention thresholds and conditions
"""
    
    def _build_user_prompt(
        self,
        prompt: str,
        key_mappings: List[Dict[str, Any]],
        relevant_policies: List[str]
    ) -> str:
        parts = []
        
        parts.append(f"## User Request\n{prompt}")
        
        if key_mappings:
            mappings_text = "\n".join([
                f"  - \"{m['user_phrase']}\" → {m['mapped_to']} (similarity: {m['similarity']:.2f})"
                for m in key_mappings[:8] 
            ])
            parts.append(f"\n## Suggested Field Mappings\n{mappings_text}")
        
        if relevant_policies:
            policy_text = "\n---\n".join(relevant_policies[:3])
            parts.append(f"\n## Relevant Policies\n{policy_text}")
        
        parts.append("""
## Your Task
Generate the JSON Logic rule based on the user's request.
Use the suggested field mappings to identify which fields to use.
Consider the policy guidelines when choosing thresholds.
Respond with valid JSON only.""")
        
        return "\n".join(parts)
    
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        try:
            result = json.loads(response_text)
        except json.JSONDecodeError:
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                result = json.loads(json_match.group())
            else:
                raise ValueError("Could not parse LLM response as JSON")
        
        if "json_logic" not in result:
            raise ValueError("Response missing 'json_logic' field")
        
        if "explanation" not in result:
            result["explanation"] = "Rule generated from prompt."
        
        if "used_keys" not in result:
            # Extract keys from the JSON Logic
            result["used_keys"] = self._extract_keys_from_rule(result["json_logic"])
        
        return result
    
    def _extract_keys_from_rule(self, rule: Any) -> List[str]:
        keys = []
        
        if isinstance(rule, dict):
            if "var" in rule:
                keys.append(rule["var"])
            else:
                for value in rule.values():
                    keys.extend(self._extract_keys_from_rule(value))
        elif isinstance(rule, list):
            for item in rule:
                keys.extend(self._extract_keys_from_rule(item))
        
        return list(set(keys))  # Remove duplicates
    
    def _validate_rule(self, rule: Any):
        used_keys = self._extract_keys_from_rule(rule)
        
        invalid_keys = [k for k in used_keys if k not in self.valid_keys]
        
        if invalid_keys:
            suggestions_text = []
            for invalid_key in invalid_keys[:3]:
                suggestions = self.embedding_service.get_suggestions_for_unknown_field(invalid_key)
                suggestions_str = ", ".join([
                    f"{s['value']} ({s['similarity']:.2f})"
                    for s in suggestions
                ])
                suggestions_text.append(f"  '{invalid_key}' → Did you mean: {suggestions_str}")
            
            raise ValueError(
                f"Rule contains invalid field(s): {invalid_keys}. "
                f"Suggestions:\n" + "\n".join(suggestions_text)
            )
    
    def _calculate_confidence(
        self, 
        key_mappings: List[Dict[str, Any]], 
        used_keys: List[str]
    ) -> float:
        if not used_keys:
            return 0.0
        
        mapping_scores = {m["mapped_to"]: m["similarity"] for m in key_mappings}
        scores = []
        for key in used_keys:
            if key in mapping_scores:
                scores.append(mapping_scores[key])
            else:
                scores.append(0.5)
        
        avg_score = sum(scores) / len(scores) if scores else 0.0
        return min(1.0, max(0.0, avg_score))