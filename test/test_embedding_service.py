"""
Unit Tests for Embedding Service
================================
Testing the embedding and key matching logic independently of the API.

These tests don't need the server running - just run:
    pytest tests/test_embedding_service.py -v
"""

import pytest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.embedding_service import EmbeddingService
from app.config.store_keys import SAMPLE_STORE_KEYS


class TestEmbeddingService:
    @pytest.fixture
    def embedding_service(self):
        service = EmbeddingService(store_keys=SAMPLE_STORE_KEYS)
        service.initialize_key_embeddings()
        return service
    
    def test_initialization(self, embedding_service):
        assert embedding_service.key_embeddings is not None
        assert len(embedding_service.key_texts) == len(SAMPLE_STORE_KEYS)
        assert embedding_service.key_embeddings.shape[0] == len(SAMPLE_STORE_KEYS)
    
    def test_embed_text(self, embedding_service):
        embedding = embedding_service.embed_text("credit score")
        assert isinstance(embedding, np.ndarray)
        assert embedding.ndim == 1
        assert embedding.shape[0] > 0
    
    def test_embed_texts_batch(self, embedding_service):
        
        texts = ["credit score", "business age", "monthly income"]
        embeddings = embedding_service.embed_texts(texts)
        
        assert embeddings.shape[0] == 3
        assert embeddings.ndim == 2
    
    def test_cosine_similarity(self, embedding_service):
        
        vec1 = embedding_service.embed_text("credit score")
        vec2 = embedding_service.embed_text("bureau score")
        vec3 = embedding_service.embed_text("pizza delivery")
        
        sim_similar = embedding_service.cosine_similarity(vec1, vec2)
        sim_different = embedding_service.cosine_similarity(vec1, vec3)
        
        assert sim_similar > sim_different
    
    def test_find_relevant_keys_credit_score(self, embedding_service):
        
        mappings = embedding_service.find_relevant_keys(
            prompt="Approve if credit score is above 700",
            top_k=3
        )
        
        found_keys = [m["mapped_to"] for m in mappings]
        assert "bureau.score" in found_keys
    
    def test_find_relevant_keys_business_vintage(self, embedding_service):
        mappings = embedding_service.find_relevant_keys(
            prompt="Business age must be at least 2 years",
            top_k=3
        )
        
        found_keys = [m["mapped_to"] for m in mappings]
        assert "business.vintage_in_years" in found_keys
    
    def test_find_relevant_keys_multiple_fields(self, embedding_service):
        mappings = embedding_service.find_relevant_keys(
            prompt="Approve if bureau score > 700 and business vintage at least 3 years and applicant age between 25 and 60",
            top_k=5
        )
        
        found_keys = [m["mapped_to"] for m in mappings]
        assert "bureau.score" in found_keys
        assert "business.vintage_in_years" in found_keys
        assert "primary_applicant.age" in found_keys
    
    def test_find_relevant_keys_income(self, embedding_service):
        mappings = embedding_service.find_relevant_keys(
            prompt="Monthly income should be greater than 50000",
            top_k=3
        )
        
        found_keys = [m["mapped_to"] for m in mappings]
        assert "primary_applicant.monthly_income" in found_keys
    
    def test_find_relevant_keys_dpd(self, embedding_service):
        mappings = embedding_service.find_relevant_keys(
            prompt="Flag if days past due exceeds 90",
            top_k=3
        )
        
        found_keys = [m["mapped_to"] for m in mappings]
        assert "bureau.dpd" in found_keys
    
    def test_similarity_threshold(self, embedding_service):
        mappings_high = embedding_service.find_relevant_keys(
            prompt="credit score",
            top_k=10,
            threshold=0.7
        )
        mappings_low = embedding_service.find_relevant_keys(
            prompt="credit score",
            top_k=10,
            threshold=0.1
        )
        
        assert len(mappings_low) >= len(mappings_high)
    
    def test_suggestions_for_unknown_field(self, embedding_service):
        suggestions = embedding_service.get_suggestions_for_unknown_field(
            "loan amount",
            top_k=3
        )
        
        assert len(suggestions) == 3
        
        for s in suggestions:
            assert "value" in s
            assert "label" in s
            assert "similarity" in s
    
    def test_extract_field_phrases(self, embedding_service):
        phrases = embedding_service._extract_field_phrases(
            "Approve if bureau score > 700 and business vintage at least 3 years"
        )
        
        assert len(phrases) > 0
        assert any("score" in p.lower() or "bureau" in p.lower() for p in phrases)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])