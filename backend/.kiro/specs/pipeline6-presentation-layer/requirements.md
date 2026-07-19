# Requirements Document

## Introduction

The Pipeline 6 presentation layer redesign transforms the JobPilot AI job search system's presentation logic into a pure adapter pattern implementation. This feature separates presentation logic from decision-making, ensuring that Pipeline 6 only formats and aggregates data produced by Pipeline 4, without re-evaluating or determining match decisions. The redesign introduces a new MatchSummaryDTO structure and removes dependencies on legacy database fields.

## Glossary

- **Pipeline 6**: The presentation layer component responsible for formatting and aggregating job search results for frontend display
- **Pipeline 4**: The comparison layer component responsible for determining match decisions and storing them in ComparisonEvidence
- **ComparisonEvidence**: A data structure produced by Pipeline 4 containing deterministic evidence items and scores for candidate-job matching
- **MatchSummaryDTO**: A Data Transfer Object that aggregates and formats comparison evidence for frontend presentation
- **JobCardDTO**: The main DTO containing job metadata, match summary, and AI insights for frontend display

## Requirements

### Requirement 1

**User Story:** As a frontend developer, I want consistent and reliable job match data formatting, so that the UI can display job recommendations with clear matching and missing skills/capabilities.

#### Acceptance Criteria

1. WHEN the presentation layer processes job search results, THEN THE Pipeline 6 SHALL retrieve ComparisonEvidence from JobSearchResult objects
2. WHERE technology evidence items exist, THE Pipeline 6 SHALL format matching_skills and missing_skills lists based on match_type values
3. WHERE capability evidence items exist, THE Pipeline 6 SHALL format matching_capabilities and missing_capabilities lists based on match_type values
4. WHILE aggregating comparison evidence, THE Pipeline 6 SHALL compute technology_match_count and capability_match_count statistics
5. IF alignment evidence exists for experience, education, or domain, THEN THE Pipeline 6 SHALL convert alignment enums to presentation booleans

### Requirement 2

**User Story:** As a system architect, I want clean separation between decision-making and presentation logic, so that match determinations remain exclusively in Pipeline 4.

#### Acceptance Criteria

1. WHEN Pipeline 6 executes presentation logic, THEN THE Pipeline 6 SHALL NOT re-evaluate or determine match decisions
2. WHERE match decisions are required for presentation, THE Pipeline 6 SHALL use pre-computed values from ComparisonEvidence
3. WHILE Pipeline 6 formats evidence, THE system SHALL maintain the deterministic nature of Pipeline 4's match decisions
4. IF alignment enums need to be presented, THEN THE Pipeline 6 SHALL map them to boolean values without altering match logic

### Requirement 3

**User Story:** As a backend developer, I want to remove legacy field dependencies, so that the system uses only structured comparison evidence for presentation.

#### Acceptance Criteria

1. WHEN constructing MatchSummaryDTO, THEN THE Pipeline 6 SHALL NOT read matching_skills or missing_skills database columns
2. WHERE legacy database fields exist, THE system SHALL ignore them in favor of structured ComparisonEvidence
3. WHILE processing job search results, THE Pipeline 6 SHALL use only ComparisonEvidence JSON for match data
4. IF ComparisonEvidence is null or empty, THEN THE Pipeline 6 SHALL provide safe default values for match summary fields

### Requirement 4

**User Story:** As a product owner, I want enhanced job recommendation displays, so that users can see both technical skills and professional capabilities matches.

#### Acceptance Criteria

1. WHEN presenting job recommendations, THEN THE MatchSummaryDTO SHALL include matching_capabilities and missing_capabilities fields
2. WHERE capability evidence items exist, THE frontend SHALL display them in a structured capabilities section
3. WHILE aggregating match data, THE system SHALL maintain separate counts for technology and capability matches
4. IF the frontend requests job data, THEN THE response SHALL include complete match summary information in the new DTO structure

### Requirement 5

**User Story:** As a DevOps engineer, I want improved observability for pipeline execution, so that I can debug and validate presentation layer performance.

#### Acceptance Criteria

1. WHEN Pipeline 6 executes, THEN THE system SHALL log input summaries and execution times
2. WHERE presentation errors occur, THE system SHALL provide structured error information with context
3. WHILE processing multiple job results, THE Pipeline 6 SHALL track and report completion status
4. IF presentation aggregation fails, THEN THE system SHALL provide fallback mechanisms to maintain response integrity
