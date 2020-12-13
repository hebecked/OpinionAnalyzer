select hdr.url, cmt.body, count(distinct(cmt.id)) as comment_count, count(distinct(hdr.id)) as hdr_count from news_meta_data.comment as cmt, news_meta_data.article_header as hdr, news_meta_data.article_body as bdy
where bdy.article_id=hdr.id and bdy.id=cmt.article_body_id
group by cmt.body,hdr.url having count(distinct(cmt.id))>1 order by comment_count desc