--delete all records from analyzer_log table that have no end_timestap, call with parameter: analyzer_id

CREATE OR REPLACE PROCEDURE news_meta_data.analyzer_log_cleanup(IN analyzer_id_p news_meta_data.analyzer_log.analyzer_id%TYPE)
LANGUAGE SQL
AS $$
delete
from news_meta_data.analyzer_log
where end_timestamp is null
and analyzer_id=analyzer_id_p;
$$;