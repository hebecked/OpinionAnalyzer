BEGIN;

ALTER TABLE news_meta_data.source_header ADD FOREIGN KEY (type) REFERENCES news_meta_data.source_type_header (id);
ALTER TABLE news_meta_data.article_header ADD FOREIGN KEY (source_id) REFERENCES news_meta_data.source_header (id);
ALTER TABLE news_meta_data.article_body ADD FOREIGN KEY (article_id) REFERENCES news_meta_data.article_header (id) ON DELETE CASCADE;
ALTER TABLE news_meta_data.udf_values ADD FOREIGN KEY (udf_id) REFERENCES news_meta_data.udf_header (id);
ALTER TABLE news_meta_data.udf_values ADD FOREIGN KEY (object_type) REFERENCES news_meta_data.object_header (id);
ALTER TABLE news_meta_data.comment ADD FOREIGN KEY (article_body_id) REFERENCES news_meta_data.article_body (id) ON DELETE CASCADE;
ALTER TABLE news_meta_data.crawl_log ADD FOREIGN KEY (source_id) REFERENCES news_meta_data.source_header (id);
ALTER TABLE news_meta_data.analyzer_log ADD FOREIGN KEY (analyzer_id) REFERENCES news_meta_data.analyzer_header (id);
ALTER TABLE news_meta_data.analyzer_log ADD FOREIGN KEY (analyzer_id) REFERENCES news_meta_data.analyzer_header (id);
ALTER TABLE news_meta_data.analyzer_log ADD FOREIGN KEY (comment_id) REFERENCES news_meta_data.comment (id);
ALTER TABLE news_meta_data.analyzer1_result ADD FOREIGN KEY (analyzer_log_id) REFERENCES news_meta_data.analyzer_log (id);

COMMIT;
