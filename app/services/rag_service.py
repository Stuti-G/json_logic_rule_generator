import numpy as np
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class RAGService:
    def __init__(self, embedding_service, policy_documents: List[str]):
        self.embedding_service = embedding_service
        self.policy_documents = policy_documents
        self.policy_embeddings: Optional[np.ndarray] = None

    def initialize_policy_embeddings(self):
        logger.info("Computing embeddings for policy documents...")

        self.chunks = []
        for doc in self.policy_documents:
            paragraphs = doc.strip().split("\n\n")
            for para in paragraphs:
                para = para.strip()
                if len(para) > 50:
                    self.chunks.append(para)

        logger.info(
            f"Created {len(self.chunks)} chunks from {len(self.policy_documents)} documents"
        )

        self.policy_embeddings = self.embedding_service.embed_texts(self.chunks)

        logger.info("Policy embeddings computed successfully")

    def retrieve_relevant_policies(
        self, query: str, top_k: int = 3, threshold: float = 0.2
    ) -> List[str]:
        if self.policy_embeddings is None:
            logger.warning("Policy embeddings not initialized, skipping RAG")
            return []

        query_embedding = self.embedding_service.embed_text(query)

        similarities = np.dot(self.policy_embeddings, query_embedding)

        # Get top-k chunks above threshold
        top_indices = np.argsort(similarities)[::-1][: top_k * 2]

        relevant_chunks = []
        for idx in top_indices:
            if len(relevant_chunks) >= top_k:
                break

            similarity = similarities[idx]
            if similarity >= threshold:
                relevant_chunks.append(self.chunks[idx])
                logger.debug(f"Retrieved chunk with similarity {similarity:.3f}")

        return relevant_chunks

    def get_policy_context(self, query: str, max_tokens: int = 1000) -> str:
        relevant = self.retrieve_relevant_policies(query, top_k=5)

        if not relevant:
            return ""

        context_parts = ["## Relevant Policy Guidelines:\n"]

        total_chars = 0
        max_chars = max_tokens * 4

        for i, chunk in enumerate(relevant, 1):
            chunk_text = f"\n{i}. {chunk}\n"

            if total_chars + len(chunk_text) > max_chars:
                break

            context_parts.append(chunk_text)
            total_chars += len(chunk_text)

        return "".join(context_parts)

    def add_document(self, document: str):
        paragraphs = document.strip().split("\n\n")
        new_chunks = [p.strip() for p in paragraphs if len(p.strip()) > 50]

        if not new_chunks:
            return

        new_embeddings = self.embedding_service.embed_texts(new_chunks)

        self.chunks.extend(new_chunks)

        if self.policy_embeddings is not None:
            self.policy_embeddings = np.vstack([self.policy_embeddings, new_embeddings])
        else:
            self.policy_embeddings = new_embeddings

        logger.info(f"Added {len(new_chunks)} new policy chunks")
