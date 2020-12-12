BEGIN;

--do not change order of inserts
INSERT INTO news_meta_data.source_type_header (type) VALUES('api');
INSERT INTO news_meta_data.source_type_header (type) VALUES('crawl');
--requires api to be inserted ahead of all other values into source_type_header as Spiegel needs source_id = 1
INSERT INTO news_meta_data.source_header (type, source) VALUES(1,'Spiegel');
INSERT INTO news_meta_data.object_header (type) VALUES('article_body');
INSERT INTO news_meta_data.object_header (type) VALUES('comment');
INSERT INTO news_meta_data.udf_header (udf_name) VALUES('headline');
INSERT INTO news_meta_data.udf_header (udf_name) VALUES('label');
INSERT INTO news_meta_data.udf_header (udf_name) VALUES('author');
INSERT INTO news_meta_data.udf_header (udf_name) VALUES('date_created');
INSERT INTO news_meta_data.udf_header (udf_name) VALUES('date_modified');
INSERT INTO news_meta_data.udf_header (udf_name) VALUES('date_published');
INSERT INTO news_meta_data.analyzer_header (analyzer_name, analyzer_table_name) VALUES('comment_sentiment','analyzer1_result');

COMMIT;
