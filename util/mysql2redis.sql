SELECT CONCAT(
"*3\r\n",
'$', LENGTH(redis_cmd), '\r\n',redis_cmd, '\r\n',
'$', LENGTH(redis_key), '\r\n',redis_key, '\r\n',
'$', LENGTH(hkey1), '\r\n',hkey1, '\r'
)
FROM (
 SELECT
'lpush' AS redis_cmd, 
CONCAT(code,'updown') AS redis_key,
updown AS hkey1
 FROM t_h_price where code='000001' and date>='2014-12-23'
 ) AS t1;

SELECT CONCAT(
"*3\r\n",
'$', LENGTH(redis_cmd), '\r\n',redis_cmd, '\r\n',
'$', LENGTH(redis_key), '\r\n',redis_key, '\r\n',
'$', LENGTH(hkey1), '\r\n',hkey1, '\r'
)
FROM (
 SELECT
'lpush' AS redis_cmd, 
CONCAT(code,'highest') AS redis_key,
cur AS hkey1
 FROM t_h_price where code='000001' and date>='2014-12-23'
 ) AS t1;


#where code='000001' and date>='2014-11-25' 
#echo -en '*3\r\n$5\r\nlpush\r\n$9\r\n000001cur\r\n$2\r\n10\r\n' | redis-cli --pipe
# mysql -h127.0.0.1 -uroot -p654321 -Dsat --skip-column-names --raw < /home/lzw/code/my/sat/util/mysql2redis.sql | redis-cli --pipe
#cur,updown, updownrate, highest,lowest, closed,opening, volume, turnover, turnoverrate, outdisk, indisk,earningsrate,pb, amplitude,uplimit, #downlimit,buy1, sell1, date

# redis-cli keys '*' | xargs redis-cli del
