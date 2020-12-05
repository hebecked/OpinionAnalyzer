BEGIN;

INSERT INTO news_meta_data.source_type_header (type) VALUES('api');
INSERT INTO news_meta_data.source_type_header (type) VALUES('crawl');
INSERT INTO news_meta_data.object_header (type) VALUES('article_body');
INSERT INTO news_meta_data.object_header (type) VALUES('comment');
INSERT INTO news_meta_data.udf_header (udf_name) VALUES('headline');
INSERT INTO news_meta_data.udf_header (udf_name) VALUES('label');
INSERT INTO news_meta_data.udf_header (udf_name) VALUES('author');
INSERT INTO news_meta_data.udf_header (udf_name) VALUES('date_created');
INSERT INTO news_meta_data.udf_header (udf_name) VALUES('date_modified');
INSERT INTO news_meta_data.udf_header (udf_name) VALUES('date_published');

COMMIT;
