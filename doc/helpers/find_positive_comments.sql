select 
analyzer_result.comment_id,
analyzer_result.avg_sent,
cmt.body
from
(select 
comment_id, 
avg(sentiment_value) as avg_sent,
min(sentiment_value) as min_sent
from news_meta_data.analyzer1_result 
where 
sub_id <4
group by comment_id) as analyzer_result,
news_meta_data.comment as cmt

where 
analyzer_result.min_sent >0.5 and
analyzer_result.comment_id = cmt.id

order by 
analyzer_result.avg_sent desc