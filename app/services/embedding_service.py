import numpy as np
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
import logging
import re

logger = logging.getLogger(__name__)


class EmbeddingService:
    def __init__(
        self, store_keys: List[Dict[str, str]], model_name: str = "all-MiniLM-L6-v2"
    ):
        self.store_keys = store_keys
        self.model_name = model_name

        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)

        self.key_embeddings: Optional[np.ndarray] = None
        self.key_texts: List[str] = []

    def initialize_key_embeddings(self):
        logger.info("Computing embeddings for store keys...")
        self.key_texts = []
        for key in self.store_keys:
            text = self._build_key_text(key)
            self.key_texts.append(text)
        self.key_embeddings = self.model.encode(
            self.key_texts, convert_to_numpy=True, normalize_embeddings=True
        )

        logger.info(f"Computed embeddings for {len(self.store_keys)} keys")

    def _build_key_text(self, key: Dict[str, str]) -> str:
        value = key["value"]
        label = key["label"]
        group = key["group"]
        text_parts = [label, value.replace(".", " "), group]
        synonyms = self._get_synonyms(value, label)
        text_parts.extend(synonyms)

        return " ".join(text_parts)

    def _get_synonyms(self, value: str, label: str) -> List[str]:
        synonym_map = {
            "bureau.score": [
                "credit score",
                "cibil score",
                "cibil",
                "credit rating",
                "credit bureau score",
            ],
            "bureau.dpd": [
                "days past due",
                "dpd",
                "overdue days",
                "delay days",
                "payment delay",
            ],
            "bureau.wilful_default": [
                "willful default",
                "intentional default",
                "deliberate default",
            ],
            "bureau.is_ntc": [
                "new to credit",
                "ntc",
                "no credit history",
                "first time borrower",
            ],
            "bureau.overdue_amount": [
                "outstanding amount",
                "pending amount",
                "dues",
                "arrears",
            ],
            "bureau.enquiries": [
                "credit inquiries",
                "credit checks",
                "hard pulls",
                "credit applications",
            ],
            "bureau.suit_filed": [
                "legal case",
                "court case",
                "lawsuit",
                "legal action",
            ],
            "business.vintage_in_years": [
                "business age",
                "company age",
                "years in business",
                "business duration",
                "establishment years",
                "vintage",
            ],
            "business.commercial_cibil_score": [
                "commercial credit score",
                "business credit score",
                "company cibil",
            ],
            "primary_applicant.age": [
                "applicant age",
                "customer age",
                "borrower age",
                "age",
            ],
            "primary_applicant.monthly_income": [
                "income",
                "salary",
                "monthly salary",
                "earnings",
                "monthly earnings",
            ],
            "primary_applicant.tags": [
                "applicant tags",
                "customer tags",
                "labels",
                "categories",
                "veteran",
                "employee type",
            ],
            "banking.abb": [
                "average bank balance",
                "abb",
                "average balance",
                "bank balance",
            ],
            "banking.avg_monthly_turnover": [
                "monthly turnover",
                "bank turnover",
                "account turnover",
            ],
            "banking.inward_bounces": [
                "cheque bounce",
                "check bounce",
                "inward return",
                "deposit bounce",
            ],
            "banking.outward_bounces": [
                "issued cheque bounce",
                "payment bounce",
                "outward return",
            ],
            "gst.turnover": ["gst turnover", "sales turnover", "revenue", "sales"],
            "gst.missed_returns": ["gst default", "filing default", "missed filings"],
            "gst.registration_age_months": [
                "gst age",
                "gst vintage",
                "registration duration",
            ],
            "foir": [
                "fixed obligation to income ratio",
                "foir ratio",
                "obligation ratio",
                "emi to income",
            ],
            "debt_to_income": ["dti", "debt ratio", "leverage ratio", "debt burden"],
            "itr.years_filed": ["tax returns filed", "itr filings", "income tax years"],
        }

        return synonym_map.get(value, [])

    def embed_text(self, text: str) -> np.ndarray:
        return self.model.encode(text, convert_to_numpy=True, normalize_embeddings=True)

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        return self.model.encode(
            texts, convert_to_numpy=True, normalize_embeddings=True
        )

    def cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        return float(np.dot(vec1, vec2))

    def find_relevant_keys(
        self, prompt: str, top_k: int = 5, threshold: float = 0.3
    ) -> List[Dict[str, Any]]:
        if self.key_embeddings is None:
            raise RuntimeError(
                "Key embeddings not initialized! Call initialize_key_embeddings() first."
            )

        mappings = []
        phrases = self._extract_field_phrases(prompt)

        logger.info(f"Extracted phrases from prompt: {phrases}")
        seen_keys = set()

        for phrase in phrases:
            phrase_embedding = self.embed_text(phrase)

            similarities = np.dot(self.key_embeddings, phrase_embedding)

            best_idx = np.argmax(similarities)
            best_similarity = similarities[best_idx]

            if best_similarity >= threshold:
                key_value = self.store_keys[best_idx]["value"]

                # Avoid duplicates
                if key_value not in seen_keys:
                    seen_keys.add(key_value)
                    mappings.append(
                        {
                            "user_phrase": phrase,
                            "mapped_to": key_value,
                            "similarity": float(best_similarity),
                            "label": self.store_keys[best_idx]["label"],
                        }
                    )

        prompt_embedding = self.embed_text(prompt)
        all_similarities = np.dot(self.key_embeddings, prompt_embedding)

        top_indices = np.argsort(all_similarities)[::-1][: top_k * 2]

        for idx in top_indices:
            if len(mappings) >= top_k:
                break

            key_value = self.store_keys[idx]["value"]
            similarity = all_similarities[idx]

            if key_value not in seen_keys and similarity >= threshold:
                seen_keys.add(key_value)
                mappings.append(
                    {
                        "user_phrase": "prompt_context",
                        "mapped_to": key_value,
                        "similarity": float(similarity),
                        "label": self.store_keys[idx]["label"],
                    }
                )

        # Sort by similarity (highest first)
        mappings.sort(key=lambda x: x["similarity"], reverse=True)

        return mappings[:top_k]

    def _extract_field_phrases(self, prompt: str) -> List[str]:
        phrases = []
        prompt_lower = prompt.lower()

        operator_pattern = r"([a-z_\s]+?)\s*(?:>|<|>=|<=|==|=|is|equals?|greater|less|above|below|at least|minimum|maximum)"
        matches = re.findall(operator_pattern, prompt_lower)
        phrases.extend([m.strip() for m in matches if len(m.strip()) > 2])

        with_pattern = r'(?:with|having)\s+([a-z_\s]+?)(?:\s+[\'"]|\s+>|\s+<|$)'
        matches = re.findall(with_pattern, prompt_lower)
        phrases.extend([m.strip() for m in matches if len(m.strip()) > 2])

        known_terms = [
            "credit score",
            "bureau score",
            "cibil",
            "cibil score",
            "business vintage",
            "business age",
            "company age",
            "vintage",
            "applicant age",
            "age",
            "customer age",
            "monthly income",
            "income",
            "salary",
            "dpd",
            "days past due",
            "overdue",
            "wilful default",
            "willful default",
            "default",
            "overdue amount",
            "outstanding",
            "turnover",
            "gst turnover",
            "revenue",
            "bank balance",
            "abb",
            "bounces",
            "cheque bounce",
            "foir",
            "debt to income",
            "tags",
            "veteran",
            "new to credit",
            "ntc",
        ]

        for term in known_terms:
            if term in prompt_lower:
                phrases.append(term)

        seen = set()
        unique_phrases = []
        for phrase in phrases:
            if phrase not in seen:
                seen.add(phrase)
                unique_phrases.append(phrase)

        return unique_phrases

    def get_suggestions_for_unknown_field(
        self, field_phrase: str, top_k: int = 3
    ) -> List[Dict[str, Any]]:
        phrase_embedding = self.embed_text(field_phrase)
        similarities = np.dot(self.key_embeddings, phrase_embedding)  # type: ignore

        top_indices = np.argsort(similarities)[::-1][:top_k]

        suggestions = []
        for idx in top_indices:
            suggestions.append(
                {
                    "value": self.store_keys[idx]["value"],
                    "label": self.store_keys[idx]["label"],
                    "similarity": float(similarities[idx]),
                }
            )

        return suggestions
