BEGIN;

ALTER TABLE news_meta_data.doc_count ADD FOREIGN KEY (lemma_id) REFERENCES news_meta_data.lemma_header (id) ON DELETE CASCADE;
ALTER TABLE news_meta_data.topic_detector_result ADD FOREIGN KEY (article_header_id) REFERENCES news_meta_data.article_header (id) ON DELETE CASCADE;
ALTER TABLE news_meta_data.topic_detector_result ADD FOREIGN KEY (topic_detector_id) REFERENCES news_meta_data.topic_detector_header (id) ON DELETE CASCADE;
ALTER TABLE news_meta_data.topic_detector_result ADD FOREIGN KEY (lemma_id) REFERENCES news_meta_data.lemma_header (id) ON DELETE CASCADE;

COMMIT;
