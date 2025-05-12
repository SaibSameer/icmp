# Migration Guide

## Overview
This guide provides step-by-step instructions for migrating the existing codebase to the new directory structure.

## Prerequisites

1. **Backup**
   - Create a full backup of the current system
   - Document current file locations
   - Note all dependencies

2. **Environment Setup**
   - Set up development environment
   - Install required tools
   - Configure version control

## Migration Steps

### 1. Initial Setup

1. **Create New Directory Structure**
   ```bash
   mkdir -p backend/{core,services,database,api,utils,tests}
   mkdir -p docs/{architecture,api,development,deployment}
   ```

2. **Initialize Python Packages**
   ```bash
   touch backend/{core,services,database,api,utils,tests}/__init__.py
   ```

### 2. Core Components Migration

1. **Message Processing**
   ```bash
   # Move message processing files
   mv backend/message_processing/* backend/core/message_processing/
   ```

2. **Template System**
   ```bash
   # Move template files
   mv backend/templates/* backend/core/templates/
   ```

3. **Stage Management**
   ```bash
   # Move stage files
   mv backend/stages/* backend/core/stages/
   ```

### 3. Services Migration

1. **AI Services**
   ```bash
   # Move AI-related files
   mv backend/ai/* backend/services/ai/
   ```

2. **Messaging Services**
   ```bash
   # Move messaging files
   mv backend/messaging/* backend/services/messaging/
   ```

3. **Monitoring Services**
   ```bash
   # Move monitoring files
   mv backend/monitoring/* backend/services/monitoring/
   ```

### 4. Database Migration

1. **Configuration**
   ```bash
   # Move database config
   mv backend/db_config.py backend/database/config.py
   ```

2. **Models**
   ```bash
   # Move database models
   mv backend/models/* backend/database/models/
   ```

3. **Migrations**
   ```bash
   # Move migration files
   mv backend/migrations/* backend/database/migrations/
   ```

### 5. API Migration

1. **Routes**
   ```bash
   # Move API routes
   mv backend/routes/* backend/api/routes/
   ```

2. **Schemas**
   ```bash
   # Move API schemas
   mv backend/schemas/* backend/api/schemas/
   ```

### 6. Utilities Migration

1. **General Utilities**
   ```bash
   # Move utility files
   mv backend/utils.py backend/utils/general.py
   ```

2. **Database Utilities**
   ```bash
   # Move database utilities
   mv backend/db/* backend/utils/database.py
   ```

3. **Validation Utilities**
   ```bash
   # Move validation files
   mv backend/validation/* backend/utils/validation.py
   ```

### 7. Test Migration

1. **Unit Tests**
   ```bash
   # Move unit tests
   mv backend/tests/unit/* backend/tests/unit/
   ```

2. **Integration Tests**
   ```bash
   # Move integration tests
   mv backend/tests/integration/* backend/tests/integration/
   ```

3. **End-to-End Tests**
   ```bash
   # Move e2e tests
   mv backend/tests/e2e/* backend/tests/e2e/
   ```

## Update References

1. **Import Statements**
   - Update all import statements to reflect new structure
   - Fix relative imports
   - Update package references

2. **Configuration Files**
   - Update path references
   - Update configuration settings
   - Update environment variables

3. **Documentation**
   - Update file references
   - Update path references
   - Update examples

## Verification Steps

1. **Code Verification**
   ```bash
   # Run linting
   flake8 backend/
   
   # Run type checking
   mypy backend/
   ```

2. **Test Verification**
   ```bash
   # Run all tests
   pytest backend/tests/
   ```

3. **Functionality Verification**
   - Run manual tests
   - Verify all features
   - Check error handling

## Rollback Plan

1. **Backup Restoration**
   ```bash
   # Restore from backup
   cp -r backup/* .
   ```

2. **Configuration Restoration**
   ```bash
   # Restore configuration
   cp backup/config/* config/
   ```

3. **Database Restoration**
   ```bash
   # Restore database
   pg_restore -d database_name backup/database.dump
   ```

## Post-Migration Tasks

1. **Cleanup**
   - Remove old directories
   - Remove duplicate files
   - Clean up temporary files

2. **Documentation**
   - Update documentation
   - Add migration notes
   - Update README

3. **Monitoring**
   - Monitor system performance
   - Check error logs
   - Verify functionality

## Common Issues and Solutions

1. **Import Errors**
   - Check import paths
   - Update relative imports
   - Fix package references

2. **Configuration Issues**
   - Verify path references
   - Check environment variables
   - Update configuration files

3. **Test Failures**
   - Check test paths
   - Update test imports
   - Fix test configurations

## Support

For assistance during migration:
1. Check documentation
2. Review error logs
3. Contact development team
4. Use issue tracking system 