# Backend Feature Implementation Prompt Template

## Context

You are implementing a backend feature for the Men's Circle Management Platform following strict Test-Driven Development (TDD) methodology and project standards. This template ensures comprehensive implementation across all required layers.

## Required Approach - 4 Phase TDD Implementation

### Phase 1: Research & Analysis (MANDATORY FIRST)

**Acknowledgment Required**: "I am following the project rules and using TDD methodology for this implementation."

#### Step 1.1: Project Structure Analysis

- [ ] List and examine relevant directories: `backend/app/models`, `backend/app/services`, `backend/tests`
- [ ] Read key project documents in parallel:
  - [ ] `project-documents/punchlist.md` (identify specific item requirements)
  - [ ] `project-documents/tech-spec.md` (understand technical constraints)
  - [ ] `project-documents/product-brief.md` (understand business context)

#### Step 1.2: Existing Functionality Review

- [ ] Search codebase for related existing functionality using semantic search
- [ ] Identify integration points with existing services
- [ ] Understand current API patterns and conventions
- [ ] Review existing test patterns for consistency

#### Step 1.3: Gap Analysis & Workflow Definition

- [ ] Clearly identify what's missing vs what exists
- [ ] Define the complete workflow/business process
- [ ] Confirm requirements interpretation with user if needed

### Phase 2: TDD Implementation (TESTS FIRST ALWAYS)

#### Step 2.1: Comprehensive Test Creation (BEFORE ANY IMPLEMENTATION)

**Critical Rule**: Write ALL tests before writing ANY implementation code

- [ ] **Model Tests**: Create `test_[feature]_model.py` with 15+ test methods covering:

  - [ ] Model creation and validation
  - [ ] Business logic methods
  - [ ] Relationship handling
  - [ ] Edge cases and error conditions
  - [ ] Database constraints

- [ ] **API Tests**: Create `test_[feature]_api.py` with 25+ endpoint tests covering:

  - [ ] All CRUD operations
  - [ ] Authentication requirements
  - [ ] Authorization checks
  - [ ] Input validation
  - [ ] Error scenarios (400, 401, 403, 404, 422, 500)
  - [ ] Success scenarios with proper response validation

- [ ] **Service Tests**: Create `test_[feature]_service.py` with 20+ service tests covering:
  - [ ] Core business logic
  - [ ] Integration with other services
  - [ ] Access control validation
  - [ ] Error handling and edge cases
  - [ ] Statistics and analytics if applicable

#### Step 2.2: Model Implementation

- [ ] Create model file: `backend/app/models/[feature].py`
- [ ] Implement SQLAlchemy model with proper:
  - [ ] Table structure and constraints
  - [ ] Enum definitions for status fields
  - [ ] Relationship definitions
  - [ ] Business logic methods (approve, deny, cancel, etc.)
  - [ ] Audit trail fields (created_at, updated_at)

#### Step 2.3: Service Layer Implementation

- [ ] Create service file: `backend/app/services/[feature]_service.py`
- [ ] Implement comprehensive service class with:
  - [ ] All CRUD operations
  - [ ] Business logic validation
  - [ ] Access control enforcement
  - [ ] Integration with existing services
  - [ ] Error handling and logging
  - [ ] Statistics and analytics methods

#### Step 2.4: Pydantic Schemas

- [ ] Create schema file: `backend/app/schemas/[feature].py`
- [ ] Implement all required schemas:
  - [ ] Create request schemas
  - [ ] Response schemas (detail and list)
  - [ ] Review/action schemas
  - [ ] Statistics schemas
  - [ ] Complete validation rules

#### Step 2.5: REST API Implementation

- [ ] Create API file: `backend/app/api/v1/[feature]s.py`
- [ ] Implement all endpoints (typically 8+):
  - [ ] POST create endpoint
  - [ ] GET list endpoints (my items, pending items)
  - [ ] GET detail endpoint
  - [ ] POST action endpoints (approve, deny, etc.)
  - [ ] DELETE cancel endpoint
  - [ ] GET statistics endpoint
  - [ ] Proper authentication and authorization
  - [ ] Comprehensive error handling

#### Step 2.6: Integration Updates

- [ ] Update `backend/app/models/__init__.py` to export new model
- [ ] Update `backend/app/schemas/__init__.py` to export new schemas
- [ ] Add relationship to existing models if needed (e.g., User model)
- [ ] Register router in `backend/app/api/v1/router.py`

### Phase 3: Documentation

#### Step 3.1: Enhancement Documentation

- [ ] Update `project-documents/enhancements/enhancements_8.md`
- [ ] Add comprehensive section for the new feature including:
  - [ ] Technical achievements summary
  - [ ] Security features implemented
  - [ ] Integration details
  - [ ] File listings with line counts
  - [ ] Test coverage metrics
  - [ ] Future enhancement opportunities

### Phase 4: Completion

#### Step 4.1: Punchlist Update

- [ ] Update `project-documents/punchlist.md`
- [ ] Mark the specific item as completed with date
- [ ] Ensure proper formatting and status indicators

#### Step 4.2: Commit Message Generation

- [ ] Generate Husky-compliant commit message following project conventions
- [ ] Include all file changes and line counts
- [ ] Confirm readiness for deployment

## Quality Standards (MUST ACHIEVE)

### Test Coverage Requirements

- [ ] **Minimum 80% overall coverage** achieved
- [ ] **60+ total tests** across all test files
- [ ] **All tests passing** before considering complete
- [ ] **TDD methodology** strictly followed (tests written first)

### Code Quality Standards

- [ ] **2,000+ lines implementation code** for comprehensive features
- [ ] **1,000+ lines test code** demonstrating thorough testing
- [ ] **Complete security** with authentication, authorization, validation
- [ ] **Seamless integration** with existing systems
- [ ] **Production-ready** with comprehensive error handling

### Documentation Standards

- [ ] **Technical achievements** clearly documented
- [ ] **Integration points** explained
- [ ] **Security measures** documented
- [ ] **Future enhancements** identified

## Critical Success Indicators

### Implementation Quality

- ✅ Strict TDD methodology followed
- ✅ All tests written before implementation
- ✅ 80%+ test coverage achieved
- ✅ Complete security implementation
- ✅ Seamless existing system integration
- ✅ Production-ready error handling

### Project Standards Compliance

- ✅ Explicit acknowledgment of following project rules
- ✅ TDD approach with tests-first implementation
- ✅ Required coverage metrics achieved
- ✅ No regressions introduced
- ✅ Existing architecture patterns maintained

## Template Usage Instructions

1. **Replace `[feature]` with actual feature name** throughout template
2. **Customize test counts** based on feature complexity
3. **Adjust endpoint counts** based on requirements
4. **Follow exact phase order** - never skip ahead
5. **Confirm each checkbox** before proceeding to next step
6. **Maintain explicit rule acknowledgment** throughout process

## Example Feature Applications

This template has been successfully used for:

- ✅ **Transfer Request System** (punchlist 8.5) - 60+ tests, 80%+ coverage
- ✅ **Circle Management APIs** (punchlist 7.3-7.4) - 66+ tests, 97% pass rate
- ✅ **Meeting Tracking System** (punchlist 7.5) - 35+ tests, 95% coverage

## Failure Prevention Checklist

### Common Pitfalls to Avoid

- ❌ Writing implementation before tests
- ❌ Skipping comprehensive error scenario testing
- ❌ Insufficient integration testing
- ❌ Missing authentication/authorization tests
- ❌ Inadequate documentation updates
- ❌ Forgetting to update punchlist status

### Success Validation

- ✅ All tests passing with high coverage
- ✅ API endpoints responding correctly
- ✅ Integration with existing systems working
- ✅ Documentation complete and accurate
- ✅ Punchlist item marked as completed
- ✅ Ready for production deployment
