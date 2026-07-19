# Implementation Plan

- [ ] 1. Create MatchSummaryDTO schema and update JobCardDTO
- Add MatchSummaryDTO to app/presentation/schemas/job_search.py
- Update JobCardDTO to use match_summary: MatchSummaryDTO instead of metrics field
- Ensure proper imports and BaseModel inheritance
- _Requirements: 1.1, 1.2, 4.1, 4.4_

- [ ] 2. Update JobSearchPresentationBuilder with private aggregation methods
- [ ] 2.1 Modify build_presentation method
  - Remove database column reads for matching_skills and missing_skills
  - Add ComparisonEvidence JSON deserialization with validation
  - Use Pipeline 4's score_breakdown as authoritative scoring mechanism
  - _Requirements: 1.1, 1.2, 3.1, 3.2, 3.3_

- [ ] 2.2 Implement private evidence aggregation helpers
  - Create \_aggregate_evidence_to_summary() method for evidence processing
  - Map technology_evidence to matching_skills and missing_skills lists
  - Map capability_evidence to matching_capabilities and missing_capabilities lists
  - Convert alignment enums to presentation booleans
  - Compute technology_match_count and capability_match_count
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 2.1, 2.2_

- [ ] 2.3 Add evidence validation logic
  - Create \_validate_evidence_structure() method
  - Surface presentation errors for invalid ComparisonEvidence
  - Fail fast with clear error messages for malformed evidence
  - _Requirements: 2.1, 2.2, 3.4_

- [ ] 2.4 Enhance logging and observability
  - Add structured logging for aggregation steps
  - Log execution times for evidence processing
  - Track evidence validation success/failure rates
  - _Requirements: 5.1, 5.3, 5.4_

- [ ]\* 2.5 Write unit tests for presentation builder
  - Test evidence aggregation with various structures
  - Test validation errors for malformed evidence
  - Verify match counts and boolean conversions
  - _Requirements: 5.1, 5.2_

- [ ] 3. Update frontend components
- [ ] 3.1 Modify JobRecommendationCard component
  - Update variable assignments from job.metrics to job.match_summary
  - Change skill display logic to use new field names
  - _Requirements: 4.1, 4.2_

- [ ] 3.2 Add capabilities display section
  - Create UI section for matching_capabilities display
  - Create UI section for missing_capabilities display
  - Update styling to match existing design patterns
  - _Requirements: 4.2, 4.3_

- [ ] 3.3 Update TypeScript interfaces
  - Add MatchSummaryDTO interface definition
  - Update JobCardDTO interface to include match_summary
  - Remove deprecated metrics interface
  - _Requirements: 4.1, 4.4_

- [ ]\* 3.4 Write frontend component tests
  - Test component rendering with new DTO structure
  - Verify capabilities section displays correctly
  - Test error handling for missing match_summary
  - _Requirements: 4.2, 4.3_

- [ ] 4. Add pipeline execution logging
- [ ] 4.1 Update job_search_node.py logging
  - Add structured logging for each pipeline execution
  - Include input summaries and output summaries
  - Log execution times and completion status
  - _Requirements: 5.1, 5.3_

- [ ] 4.2 Add workspace context to logs
  - Include workspace_id in all pipeline logs
  - Add conversation_id for request tracing
  - Log final completion summary with success metrics
  - _Requirements: 5.1, 5.3_

- [ ]\* 4.3 Create logging utility tests
  - Test log formatting and context injection
  - Verify structured logging captures required fields
  - Test log aggregation and filtering
  - _Requirements: 5.1, 5.3_

- [ ] 5. Consider detailed evidence endpoint (optional exploration)
- [ ] 5.1 Explore job details endpoint design
  - Research exposing full ComparisonEvidence through dedicated endpoint
  - Design lightweight search response vs detailed evidence pattern
  - Evaluate frontend requirements for detailed evidence access
  - _Requirements: 4.4_

- [ ] 5.2 Design detailed evidence API schema
  - Create detailed job evidence DTO structure
  - Plan API endpoint routing and response format
  - Consider performance implications of detailed evidence retrieval
  - _Requirements: 4.4_

- [ ] 6. Validate and verify implementation
- [ ] 6.1 Run backend test suite
  - Execute pytest for all updated components
  - Verify no regressions in existing functionality
  - Check DTO schema validation
  - _Requirements: 5.1, 5.2_

- [ ] 6.2 Test API responses
  - Verify search API returns new DTO structure
  - Check response payload matches expected schema
  - Test error responses for invalid ComparisonEvidence
  - _Requirements: 4.4, 5.2_

- [ ] 6.3 Validate frontend rendering
  - Check job cards display matching/missing skills correctly
  - Verify capabilities sections render properly
  - Test UI responsiveness with new data structure
  - _Requirements: 4.2, 4.3_

- [ ]\* 6.4 Create end-to-end validation tests
  - Test complete pipeline execution with presentation layer
  - Verify data flow from Pipeline 4 to frontend display
  - Test error scenarios and validation failures
  - _Requirements: 5.1, 5.2, 5.4_
