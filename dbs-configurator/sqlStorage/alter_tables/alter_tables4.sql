BEGIN;

<<<<<<< HEAD
ALTER TABLE news_meta_data.crawl_dates_proc ADD CONSTRAINT crawl_dates_proc_srcid_dtproc_unique UNIQUE (source_id, date_processed);
=======
alter table news_meta_data.comment add column if not exists date_created date NULL;
>>>>>>> f873078... major update for db query speedup on analyzer results

COMMIT;
