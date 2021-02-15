select 
	count(distinct(cmt.id)) as count_comments,
	count(distinct(hdr.id)) as count_articles,
	source_id
from
	news_meta_data.comment as cmt,
	news_meta_data.article_body as bdy,
	news_meta_data.article_header as hdr
where
	cmt.article_body_id = bdy.id and
	bdy.article_id = hdr.id
group by hdr.source_id