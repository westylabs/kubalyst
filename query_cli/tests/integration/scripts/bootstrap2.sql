--
-- Create reader/writer roles for the sensitive schema tables
-- Other roles should be granted these roles to access the tables
--

USE ROLE SECURITYADMIN;

CREATE OR REPLACE ROLE ${events.role.sensitiveReader}
    COMMENT = 'Allows to read data in the Events.sensitive schema';

GRANT USAGE ON DATABASE ${events.database} TO ROLE ${events.role.sensitiveReader};
GRANT USAGE ON SCHEMA ${events.database}.SENSITIVE TO ROLE ${events.role.sensitiveReader};
GRANT SELECT ON ALL TABLES IN SCHEMA ${events.database}.SENSITIVE TO ROLE ${events.role.sensitiveReader};
GRANT SELECT ON FUTURE TABLES IN SCHEMA ${events.database}.SENSITIVE TO ROLE ${events.role.sensitiveReader};

-- This is not obvious, but if data is read with the spark connector the user has to be able to create stages in the
-- schema.
-- This is the way how spark connector works. It first creates a temporary stage, saves data to it, and later compresses
-- the data and returns it to the user.
GRANT CREATE STAGE ON SCHEMA ${events.database}.SENSITIVE TO ROLE ${events.role.sensitiveReader};

CREATE OR REPLACE ROLE ${events.role.sensitiveWriter}
              COMMENT = 'Allows to write (insert) data in the Events.sensitive schema';
GRANT INSERT ON ALL TABLES IN SCHEMA ${events.database}.SENSITIVE TO ROLE ${events.role.sensitiveWriter};
GRANT INSERT ON FUTURE TABLES IN SCHEMA ${events.database}.SENSITIVE TO ROLE ${events.role.sensitiveWriter};

CREATE OR REPLACE ROLE ${events.role.dataScientist}
              COMMENT = 'Grants read-only access to the Events.sensitive schema';
GRANT ROLE ${events.role.sensitiveReader} TO ROLE ${events.role.dataScientist};

-- Create a warehouse for data scientist
USE ROLE SYSADMIN;

CREATE OR REPLACE WAREHOUSE DATA_SCIENTIST_QUERYING_WH
    WITH WAREHOUSE_SIZE = '${ds.warehouse.size}'
    WAREHOUSE_TYPE = 'STANDARD'
    AUTO_SUSPEND = ${ds.warehouse.autoSuspendSeconds}
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE
    COMMENT = 'A warehouse for data scientists';

GRANT USAGE ON WAREHOUSE DATA_SCIENTIST_QUERYING_WH TO ROLE ${events.role.dataScientist};
