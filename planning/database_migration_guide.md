# Database Migration Guide

This guide provides instructions for running database migrations in the ICMP Events API system, including the template system migration.

## Overview

Database migrations are necessary when making structural changes to the database, such as:
- Adding or removing tables
- Changing column types
- Renaming tables or columns
- Moving data between tables

## Migration Scripts

Migration scripts are stored in the `backend/migrations/` directory and are named with a numeric prefix to indicate the order in which they should be run.

Current migration scripts:
- `01_cleanup_template_tables.sql`: Migrates data from the legacy `prompt_templates` table to the new `templates` table and drops the redundant table.

## Running Migrations

### Prerequisites

- PostgreSQL client (psql) installed
- Database connection details
- Appropriate database permissions

### Method 1: Using psql

To run a migration using the PostgreSQL command-line client:

```bash
# Connect to the database
psql -h <hostname> -U <username> -d icmp_db

# Within the psql console, run the migration script
\i backend/migrations/01_cleanup_template_tables.sql
```

## Method 2: Using Python Script

You can also use the Python database utility to run migrations:

```bash
# From the project root directory
python backend/utils/run_migration.py --file backend/migrations/01_cleanup_template_tables.sql
```

## Template Migration Specifics

The template migration (01_cleanup_template_tables.sql) performs the following steps:

1. Identifies any templates in the `prompt_templates` table that haven't been migrated to the `templates` table
2. Migrates any missing templates with proper mapping:
   - `template_text` → `content`
   - `description` → Not directly mapped (used in template_name if needed)
   - Assigns a business_id (required in the new schema)
   - Generates proper UUIDs for template_id
3. Updates any references to old template IDs in the `stages` table
4. Safely drops the `prompt_templates` table once all data is migrated

### Migration Verification

To verify the migration was successful:

1. Check that all templates are present in the new table:
   ```sql
   SELECT COUNT(*) FROM templates;
   ```

2. Confirm the old table no longer exists:
   ```sql
   \dt prompt_templates;
   ```
   Should return "Did not find any relation named 'prompt_templates'."

3. Verify stage template references are intact:
   ```sql
   SELECT COUNT(*) FROM stages WHERE 
     stage_selection_template_id IS NOT NULL OR 
     data_extraction_template_id IS NOT NULL OR 
     response_generation_template_id IS NOT NULL;
   ```

## Troubleshooting

### Common Issues

1. **Permission Denied**:
   - Ensure the database user has sufficient permissions
   - Contact your database administrator if needed

2. **Failed Migration**:
   - Check the error message for details
   - Migrations are designed to be idempotent, so you can fix the issue and try again

3. **Missing Templates After Migration**:
   - Run the verification query to check if templates were successfully migrated
   - Check if business_id assignment was correct

### Rollback

If you need to rollback the template migration:

```sql
-- Note: Only use if absolutely necessary and you have backed up the data
-- This will recreate the prompt_templates table (without data)
CREATE TABLE prompt_templates (
    template_id CHARACTER VARYING(255) PRIMARY KEY NOT NULL,
    template_text TEXT NOT NULL,
    description TEXT,
    variables TEXT[] NOT NULL DEFAULT '{}',
    template_name CHARACTER VARYING(255),
    template_type CHARACTER VARYING(50) DEFAULT 'stage_selection'
);
```

## Best Practices

- Always backup the database before running migrations
- Test migrations in a non-production environment first
- Run migrations during low-traffic periods
- Update application code before or in conjunction with database changes
- Document all schema changes in migration scripts
- Include both "up" and "down" migrations when possible
- Test migrations with realistic data volumes
- Monitor database performance during migrations

## Future Migrations

### Planned Schema Changes
1. Add indexes for frequently queried columns
2. Implement soft delete for templates and stages
3. Add audit logging tables
4. Optimize column types for better performance

### Migration Process
1. Create new migration script with appropriate version number
2. Test in development environment
3. Review with team
4. Schedule production deployment
5. Monitor for issues

## Related Documentation
- See [Database Schema](database_schema.md) for current schema details
- See [Implementation Guide](implementation_guide.md) for system architecture
- See [Development Roadmap](development_roadmap.md) for project timeline

Last Updated: 2025-05-12
