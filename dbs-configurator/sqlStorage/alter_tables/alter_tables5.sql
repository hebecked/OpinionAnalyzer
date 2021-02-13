BEGIN;

ALTER TABLE news_meta_data.lemma_count ADD FOREIGN KEY (article_body_id) REFERENCES news_meta_data.article_body (id) ON DELETE CASCADE;
ALTER TABLE news_meta_data.lemma_count ADD FOREIGN KEY (lemma_id) REFERENCES news_meta_data.lemma_header (id) ON DELETE CASCADE;

COMMIT;
