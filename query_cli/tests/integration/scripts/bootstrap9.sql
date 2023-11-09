USE ROLE ${events.role.dataLoader};
USE SCHEMA INFRA;

-- Returns time in minutes that indicates raw_events -> events transformation lag.
CREATE OR REPLACE PROCEDURE GET_EVENTS_TRANFORM_LAG_MINUTES()
    RETURNS DOUBLE
    LANGUAGE JAVASCRIPT
AS
$$
function execSqlWithSingleResult(sql) {
    var stmt = snowflake.createStatement({sqlText: sql})
    var rs = stmt.execute()
    rs.next()
    return rs.getColumnValue(1)
}

var has_data_in_stream = execSqlWithSingleResult("SELECT SYSTEM$STREAM_HAS_DATA('EVENTS.INFRA.RAW_EVENTS_STREAM')")
if (!has_data_in_stream) {
    return 0
}

var stream_diff_sql = "SELECT DATEDIFF('minute', SYSTEM$STREAM_GET_TABLE_TIMESTAMP('EVENTS.INFRA.RAW_EVENTS_STREAM')::TIMESTAMP_TZ, CONVERT_TIMEZONE('UTC', CURRENT_TIMESTAMP()))"
return execSqlWithSingleResult(stream_diff_sql)
$$;

GRANT USAGE ON PROCEDURE GET_EVENTS_TRANFORM_LAG_MINUTES() TO ROLE ENG_METADATA_READER;
