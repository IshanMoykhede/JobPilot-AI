import hashlib

class HashService:
    @staticmethod
    def generate_hash(semantic_document: str, embedding_model: str, schema_version: str = "v1") -> str:
        """
        Deterministic SHA256 of the semantic document combined with model name and schema version.
        """
        combined = f"{semantic_document.strip()}||{embedding_model.strip()}||{schema_version.strip()}"
        return hashlib.sha256(combined.encode("utf-8")).hexdigest()
