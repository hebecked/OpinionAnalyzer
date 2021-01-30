BEGIN;

--do not change order of inserts
INSERT INTO news_meta_data.source_header (type, source) VALUES(2,'Welt');
INSERT INTO news_meta_data.source_header (type, source) VALUES(2,'FAZ');

COMMIT;
