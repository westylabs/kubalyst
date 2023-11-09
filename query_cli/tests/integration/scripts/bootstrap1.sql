--
-- Create Events database for Syslog V2 events.
-- Create sensitive schema with RAW_EVENTS and EVENTS tables.
--

-- Switch to SYSADMIN who owns all the objects
USE ROLE SYSADMIN;

CREATE DATABASE ${events.database};

USE DATABASE ${events.database};

CREATE OR REPLACE SCHEMA SENSITIVE
    COMMENT = 'Schema for sensitive data';

-- Create tables in the 'sensitive' schema
USE SCHEMA SENSITIVE;

-- Contains events loaded from the landing zone
-- RAW events additionally enriched with `org_id`, `cell`, and `insertion_timestamp`
CREATE OR REPLACE TABLE RAW_EVENTS (
    insertion_timestamp TIMESTAMP,
    org_id VARCHAR(20),
    cell VARCHAR(5),
    raw_json VARIANT);

-- Partially decomposed events which are easier to query than the RAW_EVENTS.
CREATE OR REPLACE TABLE EVENTS (
    insertion_timestamp TIMESTAMP,
    cell VARCHAR(5),
    uuid VARCHAR(50),
    timestamp TIMESTAMP,
    event_type VARCHAR(200),
    version VARCHAR(2),
    org_id VARCHAR(20),
    display_message_entry ARRAY,
    severity VARCHAR(10),
    client OBJECT,
    actor OBJECT,
    outcome OBJECT,
    target ARRAY,
    transaction OBJECT,
    debug_context OBJECT,
    authentication_context OBJECT,
    security_context OBJECT);
