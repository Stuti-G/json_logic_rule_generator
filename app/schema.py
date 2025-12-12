from typing import List, Optional

from pydantic import BaseModel, Field


class GenerateRuleRequest(BaseModel):
    prompt: str = Field(
        ...,
        description="Natural language description of the rule to generate",
        example="Approve if bureau score > 700 and business vintage at least 3 years",
    )  # type: ignore
    context_docs: Optional[List[str]] = Field(
        default=None, description="Optional additional policy documents for context"
    )


class KeyMapping(BaseModel):
    user_phrase: str = Field(..., description="The phrase extracted from user's prompt")
    mapped_to: str = Field(
        ..., description="The SAMPLE_STORE_KEY value we mapped it to"
    )
    similarity: float = Field(..., description="Cosine similarity score (0-1)")


class GenerateRuleResponse(BaseModel):
    json_logic: dict = Field(..., description="The generated JSON Logic rule")
    explanation: str = Field(..., description="Plain English explanation of the rule")
    used_keys: List[str] = Field(..., description="List of keys used in the rule")
    key_mappings: List[KeyMapping] = Field(
        ..., description="How user phrases mapped to keys"
    )
    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Overall confidence in the generated rule (0-1)",
    )
    rag_context_used: Optional[List[str]] = Field(
        default=None, description="Policy document IDs that were used for context"
    )


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")
    unmapped_phrases: Optional[List[str]] = Field(
        default=None, description="Phrases we couldn't map to any key"
    )
    suggestions: Optional[List[dict]] = Field(
        default=None,
        description="Suggested keys with similarity scores for unmapped phrases",
    )
