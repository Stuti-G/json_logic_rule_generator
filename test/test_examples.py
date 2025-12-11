import asyncio
import httpx
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"


async def test_rule_generation(prompt: str, test_name: str) -> Dict[str, Any]:
    print(f"\n{'='*60}")
    print(f"TEST: {test_name}")
    print(f"{'='*60}")
    print(f"\n📝 Prompt: {prompt}")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BASE_URL}/generate-rule",
                json={"prompt": prompt},
                timeout=60.0
            )
            response.raise_for_status()
            result = response.json()
            
            print("\nSuccess!")
            print(f"\nJSON Logic:\n{json.dumps(result['json_logic'], indent=2)}")
            print(f"\nExplanation: {result['explanation']}")
            print(f"\nUsed Keys: {result['used_keys']}")
            print(f"\nConfidence Score: {result['confidence_score']}")
            
            if result.get('key_mappings'):
                print("\nKey Mappings:")
                for mapping in result['key_mappings']:
                    print(f"   • \"{mapping['user_phrase']}\" → {mapping['mapped_to']} (similarity: {mapping['similarity']:.4f})")
            
            return result
            
        except httpx.HTTPStatusError as e:
            print(f"\nHTTP Error: {e.response.status_code}")
            print(f"   Detail: {e.response.text}")
            return None # type: ignore
        except Exception as e:
            print(f"\nError: {str(e)}")
            return None # type: ignore


async def run_all_tests():
    
    await test_rule_generation(
        prompt="Approve if bureau score > 700 and business vintage at least 3 years and applicant age between 25 and 60.",
        test_name="Example 1 - AND conditions with age range"
    )
    
    await test_rule_generation(
        prompt="Flag as high risk if wilful default is true OR overdue amount > 50000 OR bureau.dpd >= 90.",
        test_name="Example 2 - OR conditions for high risk"
    )
    
    await test_rule_generation(
        prompt="Prefer applicants with tag 'veteran' OR with monthly_income > 1,00,000.",
        test_name="Example 3 - Tag check with income OR"
    )
    
    await test_rule_generation(
        prompt="Reject if GST missed returns > 2 or high risk suppliers count > 3.",
        test_name="Example 4 - GST compliance check"
    )
    
    await test_rule_generation(
        prompt="Approve if FOIR is less than 0.5 and debt to income ratio below 0.4.",
        test_name="Example 5 - Financial ratios"
    )
    
    await test_rule_generation(
        prompt="Flag for review if inward bounces > 3 or outward bounces > 2.",
        test_name="Example 6 - Banking bounces"
    )
    
    await test_rule_generation(
        prompt="Approve if credit score >= 650, business is at least 2 years old, no suit filed, and applicant is between 21 and 65 years old.",
        test_name="Example 7 - Complex approval rule"
    )
    
    await test_rule_generation(
        prompt="Reject application if the cibil score is below 550 or the company age is less than 1 year.",
        test_name="Example 8 - Natural language synonyms"
    )
if __name__ == "__main__":
    
    asyncio.run(run_all_tests())