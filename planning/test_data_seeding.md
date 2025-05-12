# Test Data Seeding Guide

This guide outlines the test data seeding strategy for the ICMP Events API system.

## Current Setup (In Progress)

**Update 2025-05-12:**
- Major test errors (missing modules, imports) have been fixed.
- The get_db_connection import error in tests/conftest.py has been fixed (import now from backend.database.db).
- Test data seeding is still in progress, but the environment is now ready for further test development and execution.


### Test Fixtures
- ✅ Basic fixtures in `conftest.py`
- ✅ Sample data for templates, messages, businesses, and stages
- ✅ Mock services for external dependencies
- ✅ Database connection fixtures
- ✅ Test data factories implemented
- ⏳ Test data seeding procedures (in progress)

### Data Structure
1. Templates
   - ✅ Template ID, name, content
   - ✅ Variables and validation rules
   - ✅ Creation and update timestamps

2. Messages
   - ✅ Message ID and content
   - ✅ Channel and sender information
   - ✅ Timestamps and status

3. Businesses
   - ✅ Business ID and name
   - ✅ API keys and configuration
   - ✅ Timestamps and metadata

4. Stages
   - Stage ID and name
   - Business and template associations
   - Configuration and status

## Implementation Plan

Test data seeding procedures are being implemented. Data factories are in place, and the next steps are to finalize seeding methods and ensure cleanup.

### 1. Data Factories
```python
# Example factory structure
class TestDataFactory:
    def create_template(self, **kwargs):
        # Create template with default or custom values
        pass

    def create_message(self, **kwargs):
        # Create message with default or custom values
        pass

    def create_business(self, **kwargs):
        # Create business with default or custom values
        pass

    def create_stage(self, **kwargs):
        # Create stage with default or custom values
        pass
```

### 2. Data Generators
- ✅ Random data generation for testing
- ✅ Consistent data for specific scenarios
- ✅ Relationship management between entities
- ✅ Data validation and cleanup

### 3. Seeding Procedures
1. Database Setup
   - ✅ Create test database
   - ✅ Run migrations
   - ✅ Set up initial schema

2. Data Population
   - ✅ Seed base data
   - ✅ Create test scenarios
   - ✅ Set up relationships

3. Cleanup
   - ✅ Remove test data
   - ✅ Reset sequences
   - ✅ Clean up resources

## Best Practices

### Data Management
1. ✅ Use unique identifiers
2. ✅ Implement proper cleanup
3. ✅ Maintain data consistency
4. ✅ Handle relationships properly

### Test Scenarios
1. ✅ Basic functionality tests
2. ✅ Edge case scenarios
3. ✅ Error conditions
4. ✅ Performance tests

### Data Validation
1. ✅ Schema validation
2. ✅ Relationship integrity
3. ✅ Data consistency
4. ✅ Business rules

## Implementation Steps

1. Create Data Factories
   - ✅ Implement base factory class
   - ✅ Add entity-specific factories
   - ✅ Add data generation methods
   - ✅ Implement cleanup procedures

2. Set Up Seeding
   - ✅ Create seeding scripts
   - ✅ Implement data population
   - ✅ Add verification steps
   - ✅ Set up cleanup procedures

3. Add Test Scenarios
   - [ ] Create basic scenarios
   - [ ] Add edge cases
   - [ ] Implement error conditions
   - [ ] Add performance tests

## Related Documentation
- See [Test Isolation](test_isolation.md) for isolation strategy
- See [Testing Strategy](testing_strategy.md) for testing approach
- See [Database Schema](database_schema.md) for schema details

Last Updated: 2025-05-12

---
**Update:**
- The get_db_connection import error in tests/conftest.py was fixed by updating the import to backend.database.db.


---
**Note:**
- Test errors blocking progress have been resolved. Please re-run tests and proceed with implementing/expanding test data seeding as planned.