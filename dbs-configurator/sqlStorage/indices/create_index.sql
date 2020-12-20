BEGIN;

CREATE INDEX ah_id ON news_meta_data.article_header(id);
CREATE INDEX ab_id ON news_meta_data.article_body(id);
CREATE INDEX co_id ON news_meta_data.comment(id);
CREATE INDEX uv_otid_oid ON news_meta_data.udf_values(object_type, object_id);
CREATE INDEX uv_id ON news_meta_data.udf_values(id);
CREATE INDEX a1r_cid_al1rid ON news_meta_data.analyzer1_result(comment_id, analyzer_log_id);
CREATE INDEX a1r_id ON news_meta_data.analyzer1_result(id);
CREATE INDEX al_id ON news_meta_data.analyzer_log(id);
CREATE INDEX al_cid_alid ON news_meta_data.analyzer_log(comment_id, analyzer_id);

COMMIT;
