-- SELECT "Code" FROM price_kor LIMIT 30;

-- SELECT "Date", "Code", "Name", "Close", "Low", "High" FROM price_kor LIMIT 30;

-- SELECT "Date", "Code", "Name", "Close", "Low", "High" 
-- FROM price_kor 
-- WHERE "Code"='005930'
-- LIMIT 30;

-- select * from pg_get_keywords();

select * from pg_indexes where tablename = 'price_kor';


-- CREATE INDEX index1
-- ON price_kor ("Date", "Code");


SELECT DISTINCT("Code") FROM price_kor
WHERE "Date" >= '2019-01-01';