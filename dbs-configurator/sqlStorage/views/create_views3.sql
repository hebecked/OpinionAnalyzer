BEGIN;

--drop v_todo_analyzer1_next
DROP VIEW IF EXISTS news_meta_data.v_todo_analyzer1_next;

--drop v_todo_analyzer1
DROP VIEW IF EXISTS news_meta_data.v_todo_analyzer1;

--analyzer_log todo list analyzer1
CREATE OR REPLACE VIEW news_meta_data.v_todo_analyzer1 as (
 SELECT c.id AS comment_id,
    c.level AS comment_level,
    c.body AS comment_body,
    c.date_created as source_date,
    al.analyzer_id,
    al.start_timestamp,
    al.end_timestamp,
    al.success,
        CASE
            WHEN al.id IS NULL THEN 'new'::text
            ELSE 're-run'::text
        END AS status
   FROM news_meta_data.comment c
     LEFT JOIN news_meta_data.analyzer_log al ON c.id = al.comment_id
  WHERE al.id IS NULL 
  AND c.date_created is not null
ORDER BY c.level ASC, source_date DESC
);

--top 1000 of todo_analyzer1
CREATE OR REPLACE VIEW news_meta_data.v_todo_analyzer1_next AS (
SELECT
comment_id,
comment_level,
comment_body,
source_date,
analyzer_id,
start_timestamp,
end_timestamp,
success,
status
FROM news_meta_data.v_todo_analyzer1
WHERE start_timestamp is null
LIMIT 1000
);

COMMIT;