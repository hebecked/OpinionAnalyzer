BEGIN;

ALTER TABLE news_meta_data.doc_count DROP CONSTRAINT doc_count_lemma_id_fkey;
ALTER TABLE news_meta_data.doc_count DROP CONSTRAINT doc_count_lemma_id_mth_published_unique;
ALTER TABLE news_meta_data.doc_count DROP CONSTRAINT doc_count_pkey;
DROP TABLE news_meta_data.doc_count;

COMMIT;
