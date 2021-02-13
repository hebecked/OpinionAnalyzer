BEGIN;

INSERT INTO news_meta_data.crawl_dates_proc (source_id, date_processed)
select distinct source_id, source_date
from news_meta_data.article_header
ON CONFLICT DO NOTHING;

COMMIT;