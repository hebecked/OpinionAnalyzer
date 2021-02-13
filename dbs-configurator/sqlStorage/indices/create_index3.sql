BEGIN;

CREATE INDEX lc_article_body_id ON news_meta_data.lemma_count(article_body_id);
CREATE INDEX lc_lemma_id ON news_meta_data.lemma_count(lemma_id);

COMMIT;
