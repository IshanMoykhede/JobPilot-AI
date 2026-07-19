import logging
from typing import Optional, Dict
from app.matching.schemas.comparison import MatchType

logger = logging.getLogger(__name__)

# Predefined canonical alias mappings (alias -> canonical)
CANONICAL_ALIASES: Dict[str, str] = {
    "reactjs": "React",
    "react.js": "React",
    "react": "React",
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "js": "JavaScript",
    "javascript": "JavaScript",
    "ts": "TypeScript",
    "typescript": "TypeScript",
    "nextjs": "Next.js",
    "next.js": "Next.js",
    "node": "Node.js",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "docker": "Docker",
    "k8s": "Kubernetes",
    "kubernetes": "Kubernetes",
    "fastapi": "FastAPI",
    "aws": "AWS",
    "amazon web services": "AWS",
    "gcp": "GCP",
    "google cloud": "GCP",
    "google cloud platform": "GCP",
    "azure": "Azure",
    "microsoft azure": "Azure",
    "mongodb": "MongoDB",
    "redis": "Redis",
    "mysql": "MySQL",
    "sqlite": "SQLite",
    "github": "GitHub",
}

# Predefined partial / adjacent tech equivalents (tech -> list of related techs)
ADJACENT_EQUIVALENTS: Dict[str, list] = {
    "tensorflow": ["pytorch", "keras", "mxnet"],
    "pytorch": ["tensorflow", "keras", "mxnet"],
    "fastapi": ["flask", "django", "express.js", "nest.js", "spring boot"],
    "flask": ["fastapi", "django", "express.js", "nest.js"],
    "django": ["fastapi", "flask", "spring boot", "express.js"],
    "react": ["vue.js", "angular", "svelte", "next.js"],
    "vue.js": ["react", "angular", "svelte"],
    "angular": ["react", "vue.js", "svelte"],
    "postgresql": ["mysql", "sqlite", "oracle", "sql server", "mariadb"],
    "mysql": ["postgresql", "sqlite", "mariadb", "oracle"],
    "mongodb": ["dynamodb", "couchdb", "cassandra", "redis"],
    "redis": ["memcached", "hazelcast"],
    "aws": ["gcp", "azure", "heroku", "digitalocean"],
    "gcp": ["aws", "azure", "digitalocean"],
    "azure": ["aws", "gcp"],
}

class NormalizationMatcher:
    @staticmethod
    def evaluate_match(candidate_val: str, required_val: str) -> MatchType:
        """
        Determines the MatchType by evaluating candidate_val against required_val:
        - EXACT: case-insensitive exact string match.
        - CANONICAL: matching alias terms (synonyms).
        - PARTIAL: adjacent or equivalent technologies.
        - MISSING: no matching mapping found.
        """
        cand_clean = candidate_val.strip().lower()
        req_clean = required_val.strip().lower()

        # 1. Exact string match
        if cand_clean == req_clean:
            return MatchType.EXACT

        # 2. Canonical alias matches
        cand_canon = CANONICAL_ALIASES.get(cand_clean, cand_clean).lower()
        req_canon = CANONICAL_ALIASES.get(req_clean, req_clean).lower()
        if cand_canon == req_canon:
            return MatchType.CANONICAL

        # 3. Partial equivalents mapping check
        if cand_canon in ADJACENT_EQUIVALENTS:
            if req_canon in ADJACENT_EQUIVALENTS[cand_canon]:
                return MatchType.PARTIAL
        if req_canon in ADJACENT_EQUIVALENTS:
            if cand_canon in ADJACENT_EQUIVALENTS[req_canon]:
                return MatchType.PARTIAL

        return MatchType.MISSING
