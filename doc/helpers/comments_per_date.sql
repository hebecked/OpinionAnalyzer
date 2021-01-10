select 
	hdr.source_date as Veroeffentlichungs_Datum_Artikel, count(cmt.id) as Anzahl_Kommentare
from 
	news_meta_data.article_header as hdr,
	news_meta_data.article_body as bdy,
	news_meta_data.comment as cmt
where 
	hdr.id = bdy.article_id and
	bdy.id = cmt.article_body_id

group by hdr.source_date
order by hdr.source_date asc

