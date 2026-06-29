# Configuration for Evidence Engine Scoring

SOURCE_WEIGHTS = {
    "EXPERIENCE": 100,
    "PROJECT": 80,
    "CERTIFICATION": 50,
    "EDUCATION": 40,
    "SKILL": 20
}

# The default weight if a source type is unknown
DEFAULT_SOURCE_WEIGHT = 10

# Defines how diversity scales based on number of unique sources
DIVERSITY_RULES = {
    1: 50,
    2: 75,
    3: 100
}
DEFAULT_DIVERSITY_SCORE = 100

# Formula Weights for Confidence Score Calculation
CONFIDENCE_SOURCE_WEIGHT = 0.5
CONFIDENCE_DIVERSITY_WEIGHT = 0.3
CONFIDENCE_PRACTICAL_WEIGHT = 0.2

# Caps applied under specific conditions
CONFIDENCE_CAPS = {
    "ACADEMIC_ONLY": 70,
    "CLAIMED_ONLY": 30
}

# Scaling factors for source strength calculation
SOURCE_STRENGTH_SCALING = {
    "BASE_MULTIPLIER": 10,
    "MAX_BONUS": 50
}

# Quality mapping thresholds (lower bound inclusive)
QUALITY_THRESHOLDS = {
    "HIGH": 85,
    "MEDIUM": 60,
    "LOW": 40
}

# Thresholds for generating strengths and weaknesses
REPORTING_THRESHOLDS = {
    "HIGH_CONFIDENCE_MIN": 85,
    "MEDIUM_CONFIDENCE_MIN": 60,
    "STRONG_AREAS_MIN_COUNT": 3,
    "PRACTICAL_AREAS_MIN_COUNT": 5,
    "WEAK_CLAIMS_MIN_COUNT": 3,
    "ACADEMIC_ONLY_MIN_COUNT": 2
}
