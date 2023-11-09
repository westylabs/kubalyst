USE SCHEMA INFRA;

-- Creates views on SENSITIVE.EVENTS and SENSITIVE.RAW_EVENTS tables with minimal fields
-- exposure to allow the data lake team conduct minimal investigations
CREATE OR REPLACE SECURE VIEW NON_PRIVILEGED_EVENTS
COMMENT = 'View that exposes minimal amount of non-sensitive fields for non-privileged users'
AS SELECT INSERTION_TIMESTAMP, CELL, UUID, ORG_ID FROM SENSITIVE.EVENTS;

CREATE OR REPLACE SECURE VIEW NON_PRIVILEGED_RAW_EVENTS
COMMENT = 'View that exposes minimal amount of non-sensitive fields for non-privileged users'
AS SELECT INSERTION_TIMESTAMP, CELL, ORG_ID FROM SENSITIVE.RAW_EVENTS;

-- Switch to SECURITYADMIN who can operate on users/roles
USE ROLE SECURITYADMIN;

-- Grant ENG_METADATA_READER read from the views privileges
GRANT SELECT ON VIEW ${events.database}.INFRA.NON_PRIVILEGED_EVENTS TO ROLE ${global.role.engMetadataReader};
GRANT SELECT ON VIEW ${events.database}.INFRA.NON_PRIVILEGED_RAW_EVENTS TO ROLE ${global.role.engMetadataReader};

-- Create a roles hierarchy where all objects are accessible by SYSADMIN
-- This is a fix of the current roles hierarchy.
GRANT ROLE ${global.role.engMetadataReader} TO ROLE SYSADMIN;
