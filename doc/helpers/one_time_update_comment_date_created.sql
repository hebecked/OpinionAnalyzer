do
$$
declare
    f int;
begin
    for f in select id 
	       from news_meta_data.comment 
	       where date_created is null
	       limit 500000
    loop 
		update news_meta_data.comment co
		set date_created = TO_DATE(substring(ud.udf_value,1,10),'YYYY-MM-DD')
		from news_meta_data.udf_values ud
		where co.id=f
		and co.id=ud.object_id
		and ud.object_type=2
		and ud.udf_id=4;
    end loop;
end;
$$