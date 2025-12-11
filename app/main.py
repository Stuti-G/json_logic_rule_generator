from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging

from app.services.embedding_service import EmbeddingService
from app.services.rag_service import RAGService
from app.services.rule_generator import RuleGenerator
from app.config.store_keys import SAMPLE_STORE_KEYS
from app.config.policy_docs import POLICY_DOCUMENTS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="JSON Logic Rule Generator",
    description="AI-powered API to convert natural language into JSON Logic rules using embeddings and RAG",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RuleRequest(BaseModel):
    prompt: str
    context_docs: Optional[List[str]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "Approve if bureau score > 700 and business vintage at least 3 years",
                "context_docs": ["Minimum age requirement is 21 years"]
            }
        }


class KeyMapping(BaseModel):
    user_phrase: str
    mapped_to: str
    similarity: float


class RuleResponse(BaseModel):
    """
    The full response we send back - JSON Logic rule, explanation, and all the mappings.
    I'm including everything needed to understand and debug the generated rule.
    """
    json_logic: Dict[str, Any]
    explanation: str
    used_keys: List[str]
    key_mappings: List[KeyMapping]
    confidence_score: float
    relevant_policies: Optional[List[str]] = None

embedding_service = EmbeddingService(store_keys=SAMPLE_STORE_KEYS)

rag_service = RAGService(
    embedding_service=embedding_service,
    policy_documents=POLICY_DOCUMENTS
)

rule_generator = RuleGenerator(
    embedding_service=embedding_service,
    rag_service=rag_service,
    store_keys=SAMPLE_STORE_KEYS
)


@app.on_event("startup")
async def startup_event():
    logger.info("Starting up JSON Logic Rule Generator...")
    logger.info("Initializing embeddings for store keys...")
    
    embedding_service.initialize_key_embeddings()
    
    rag_service.initialize_policy_embeddings()
    
    logger.info("Server ready to generate rules!")


@app.get("/")
async def root():
    return {
        "status": "healthy",
        "message": "JSON Logic Rule Generator API is running",
        "version": "1.0.0"
    }

@app.post("/generate-rule", response_model=RuleResponse)
async def generate_rule(request: RuleRequest):
    logger.info(f"Received prompt: {request.prompt}")
    
    try:
        key_mappings = embedding_service.find_relevant_keys(
            prompt=request.prompt,
            top_k=10, 
            threshold=0.3  
        )
        
        logger.info(f" Found {len(key_mappings)} potential key mappings")
        combined_docs = POLICY_DOCUMENTS.copy()
        if request.context_docs:
            combined_docs.extend(request.context_docs)
        
        relevant_policies = rag_service.retrieve_relevant_policies(
            query=request.prompt,
            top_k=3
        )
        
        logger.info(f"Retrieved {len(relevant_policies)} relevant policy snippets")
        result = await rule_generator.generate(
            prompt=request.prompt,
            key_mappings=key_mappings,
            relevant_policies=relevant_policies
        )
        
        logger.info(f"Generated rule with {len(result['used_keys'])} keys")
        
        return RuleResponse(
            json_logic=result["json_logic"],
            explanation=result["explanation"],
            used_keys=result["used_keys"],
            key_mappings=[
                KeyMapping(
                    user_phrase=m["user_phrase"],
                    mapped_to=m["mapped_to"],
                    similarity=round(m["similarity"], 4)
                )
                for m in result["key_mappings"]
            ],
            confidence_score=round(result["confidence_score"], 4),
        )
        
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Error generating rule: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate rule: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)