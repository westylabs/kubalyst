--
-- This is the 1st part of snowpipe setup which uses a `storage integration`
--
-- This migration should be executed only after the `aws_landing_zone_reader_arn`
-- (role that grants the read-only access to the landing zone) has been created
-- in the AWS lake account.
--
-- After this migration has been executed, an operator should run the following
-- statement to retrieve the ARN for the AWS IAM user that was created
-- automatically for our Snowflake account, and `STORAGE_AWS_EXTERNAL_ID`, and
-- update the `aws.source.iam.readerArn` accordingly.
-- Only after that `V5__snowpipe-setup-part2.sql` can be run.
--
-- DESC INTEGRATION events_landing;
--
-- See https://oktawiki.atlassian.net/wiki/spaces/eng/pages/704905912/Data+Lake+Snowflake+Ingestion#DataLakeSnowflakeIngestion-SnowflakeaccesstoDataLakebuckets
-- for details.
--

-- Storage integration creation requires ACCOUNTADMIN privileges;
USE ROLE ACCOUNTADMIN;

CREATE OR REPLACE STORAGE INTEGRATION events_landing
    TYPE = EXTERNAL_STAGE
    STORAGE_PROVIDER = S3
    ENABLED = TRUE
    STORAGE_AWS_ROLE_ARN = '${aws.source.iam.readerArn}'
    STORAGE_ALLOWED_LOCATIONS = ('${aws.source.events.s3Path}');

-- Grant usage access on the integration to the DATA_LOADER role.
GRANT USAGE ON INTEGRATION events_landing to ROLE ${events.role.dataLoader};
