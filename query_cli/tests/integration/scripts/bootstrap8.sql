-- See [1] https://docs.snowflake.net/manuals/user-guide/security-access-control-privileges.html
-- for available permissions

USE ROLE SECURITYADMIN;

CREATE OR REPLACE ROLE ENG_METADATA_READER
    COMMENT = 'Allows to see information about various database objects, but does not allow to read the sensitive data';

-- Allows to run USE DATABASE command
GRANT USAGE ON DATABASE EVENTS TO ROLE ENG_METADATA_READER;

-- Allows to describe database
GRANT MONITOR ON DATABASE EVENTS TO ROLE ENG_METADATA_READER;

-- Allows to run USE SCHEMA command
GRANT USAGE ON SCHEMA EVENTS.INFRA TO ROLE ENG_METADATA_READER;

-- Allows to describe schema
GRANT MONITOR ON SCHEMA EVENTS.INFRA TO ROLE ENG_METADATA_READER;

-- Allows to see sensitive cleanup history
GRANT SELECT ON TABLE EVENTS.INFRA.SENSITIVE_CLEANUP_HISTORY TO ROLE ENG_METADATA_READER;

-- The following grants require ACCOUNTADMIN permissions, as they affect account.
-- See [1]
USE ROLE ACCOUNTADMIN;

-- Allows to see resources usage and billing
GRANT MONITOR USAGE ON ACCOUNT TO ROLE ENG_METADATA_READER;

-- Allows to see an execution history of any task
GRANT MONITOR EXECUTION ON ACCOUNT TO ROLE ENG_METADATA_READER;
