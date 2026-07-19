# Design Document: Pipeline 6 Presentation Layer Redesign

## Overview

The Pipeline 6 presentation layer redesign transforms the job search presentation logic into a pure adapter pattern implementation. This redesign ensures clean separation between decision-making (Pipeline 4) and presentation formatting (Pipeline 6), introduces a new structured DTO hierarchy, removes legacy field dependencies, and enhances the user interface with capability-based matching displays.

## Architecture

### Current Architecture Limitations

1. **Mixed Responsibilities**: Pipeline 6 currently reconstructs match logic by parsing and deciding rules on evidence
2. **Legacy Dependencies**: Relies on `matching_skills` and `missing_skills` database columns
3. **Schema Mismatch**: Frontend expects `metrics` field while backend provides legacy structure
4. **Limited Observability**: Minimal logging makes debugging pipeline failures difficult

### Redesigned Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Pipeline 4    │    │   Pipeline 6    │    │    Frontend     │
│  Comparison     │───▶│  Presentation   │───▶│  Components     │
│    Layer        │    │    Layer        │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                       │                       │
        ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Comparison-     │    │ MatchSummaryDTO │    │ JobCardDTO      │
│   Evidence      │    │  Aggregation    │    │  Composition    │
│ (deterministic) │    │    Logic        │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Key Design Principles

1. **Adapter Pattern**: Pipeline 6 acts as a pure adapter, transforming structured data without business logic
2. **Separation of Concerns**: Match decisions remain exclusively in Pipeline 4; presentation formatting in Pipeline 6
3. **DTO-First Design**: Frontend receives structured, predictable DTOs with clear field semantics
4. **Backward Compatibility**: Safe fallbacks for null/empty ComparisonEvidence

## Components and Interfaces

### 1. MatchSummaryDTO Schema

```python
class MatchSummaryDTO(BaseModel):
    score: float
    recommended_rank: Optional[int] = None
    matching_skills: List[str] = []
    missing_skills: List[str] = []
    matching_capabilities: List[str] = []
    missing_capabilities: List[str] = []
    technology_match_count: int = 0
    capability_match_count: int = 0
    experience_aligned: bool = False
    education_aligned: bool = False
    domain_aligned: bool = False
```

### 2. Updated JobCardDTO Composition

```python
class JobCardDTO(BaseModel):
    metadata: JobMetadataDTO
    match_summary: MatchSummaryDTO  # Replaces 'metrics' field
    insight: AIInsightDTO
```

### 3. Presentation Builder Interface

```python
class JobSearchPresentationBuilder:
    def build_presentation(
        self,
        workspace_id: UUID
    ) -> JobSearchResponse:
        # Fetch SearchWorkspace and JobSearchResult objects
        # Deserialize ComparisonEvidence from JSON with validation
        # Aggregate evidence using private helper methods
        # Construct JobCardDTO with MatchSummaryDTO
        # Log execution metrics
        # Return complete presentation response

    def _aggregate_evidence_to_summary(
        self,
        comparison_evidence: Dict
    ) -> MatchSummaryDTO:
        # Private helper method for evidence aggregation
        # Map technology_evidence to matching_skills/missing_skills
        # Map capability_evidence to matching_capabilities/missing_capabilities
        # Convert alignment enums to booleans
        # Compute match counts
        # Use Pipeline 4's score breakdown as authoritative
        # Return structured DTO

    def _validate_evidence_structure(
        self,
        evidence: Dict
    ) -> bool:
        # Validate ComparisonEvidence structure
        # Raise presentation error for invalid evidence
        # Return True if evidence is valid
```

## Data Models

### 1. ComparisonEvidence Structure (Produced by Pipeline 4)

```json
{
  "technology_evidence": [
    { "skill": "Python", "match_type": "EXACT" },
    { "skill": "Docker", "match_type": "MISSING" }
  ],
  "capability_evidence": [
    { "capability": "REST API Design", "match_type": "RELATED" },
    { "capability": "Cloud Deployments", "match_type": "MISSING" }
  ],
  "experience_evidence": { "alignment": "EXACT" },
  "education_evidence": { "alignment": "RELATED" },
  "domain_evidence": { "alignment": "PARTIAL" },
  "score_breakdown": {
    "technology_score": 85,
    "capability_score": 75,
    "experience_score": 90,
    "education_score": 80,
    "domain_score": 70,
    "overall_score": 85.0
  }
}
```

### 2. Frontend Response Structure

```json
{
  "metadata": { ... },
  "match_summary": {
    "score": 85.0,
    "recommended_rank": 1,
    "matching_skills": ["Python", "FastAPI"],
    "missing_skills": ["Docker"],
    "matching_capabilities": ["REST API Design"],
    "missing_capabilities": ["Cloud Deployments"],
    "technology_match_count": 2,
    "capability_match_count": 1,
    "experience_aligned": true,
    "education_aligned": true,
    "domain_aligned": true
  },
  "insight": { ... }
}
```

## Error Handling

### 1. Invalid ComparisonEvidence

- **Scenario**: ComparisonEvidence JSON is null, empty, or malformed
- **Strategy**: Surface a presentation error rather than rendering incomplete data
- **Implementation**: Raise validation exception with specific error details

### 2. Evidence Validation Errors

- **Scenario**: Evidence structure doesn't match expected schema
- **Strategy**: Fail fast with clear error messages
- **Implementation**: Comprehensive schema validation before aggregation

### 3. Pipeline 4 Integration

- **Scenario**: Missing or incomplete score breakdown from Pipeline 4
- **Strategy**: Use Pipeline 4's score breakdown as authoritative scoring mechanism
- **Implementation**: Trust the aggregated scores produced by Pipeline 4

## Testing Strategy

### 1. Unit Tests

- **ComparisonEvidenceAggregator**: Test aggregation logic with various evidence structures
- **MatchSummaryDTO**: Validate field mappings and calculations
- **Edge Cases**: Null evidence, missing fields, malformed JSON

### 2. Integration Tests

- **Presentation Builder**: End-to-end pipeline execution with mock data
- **Database Integration**: Verify proper data retrieval and serialization
- **Frontend Compatibility**: Ensure DTO structure matches frontend expectations

### 3. Performance Tests

- **Aggregation Performance**: Measure time to process evidence for multiple jobs
- **Memory Usage**: Monitor DTO construction memory footprint
- **Scalability**: Test with large evidence sets (100+ items)

### 4. Validation Tests

- **Schema Validation**: Ensure DTOs match OpenAPI specifications
- **Data Integrity**: Verify evidence aggregation preserves match decisions
- **Consistency**: Confirm same evidence produces identical DTOs

## Implementation Notes

### 1. Development Strategy

1. **Simultaneous Update**: Update backend and frontend together during active development
2. **Clean Break**: Avoid carrying legacy structures or backward compatibility layers
3. **Direct Integration**: Frontend immediately consumes new DTO structure

### 2. Observability Enhancements

- Structured logging for each aggregation step
- Metrics for evidence parsing success/failure rates
- Performance timings for DTO construction
- Error tracking with workspace context

### 3. Frontend Integration

- Update JobRecommendationCard component to use match_summary
- Add capabilities display section in UI
- Update TypeScript interfaces to match new DTO structure
- Consider exposing full ComparisonEvidence through dedicated job details endpoint

## Design Updates Based on Feedback

### 1. Simplified Aggregation Architecture

- **Removed ComparisonEvidenceAggregator class**: Aggregation logic kept as private helper methods within JobSearchPresentationBuilder
- **Private helper methods**: `_aggregate_evidence_to_summary()` and `_validate_evidence_structure()` handle evidence processing
- **Clean separation**: Helper methods only grow into separate class if complexity warrants it

### 2. Authoritative Scoring Mechanism

- **No per-evidence-item score fields**: Pipeline 4's `score_breakdown` serves as the authoritative scoring mechanism
- **Trust Pipeline 4**: Presentation layer uses aggregated scores produced by Pipeline 4
- **Simplified evidence items**: Evidence items contain only match_type and skill/capability data

### 3. Direct Implementation Strategy

- **No migration plan**: Since project is under active development, backend and frontend updated together
- **Clean break**: Avoid carrying legacy structures or backward compatibility layers
- **Simultaneous deployment**: Frontend immediately consumes new DTO structure

### 4. Strict Error Handling

- **No silent skipping**: Invalid ComparisonEvidence surfaces presentation errors
- **Fail fast**: Malformed evidence raises validation exceptions with clear error messages
- **Data integrity**: Ensures frontend receives complete and accurate match data

### 5. Enhanced Data Access Pattern

- **Lightweight search response**: Main search response contains aggregated MatchSummaryDTO
- **Detailed evidence endpoint**: Full ComparisonEvidence available through dedicated job details endpoint
- **Flexible access**: Frontend can request detailed evidence when needed without bloating search responses
