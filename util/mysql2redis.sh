#!/bin/bash

src_tbl='t_h_price'
#column='date'
function get_sql()
{
column=$1
curdate=$2

mysql2redis="
SELECT CONCAT(\
'*3\r\n',\
'$', LENGTH(redis_cmd), '\r\n',redis_cmd, '\r\n',\
'$', LENGTH(redis_key), '\r\n',redis_key, '\r\n',\
'$', LENGTH(hkey1), '\r\n',hkey1, '\r'\
)\
FROM (\
 SELECT\
'lpush' AS redis_cmd, \
CONCAT(code,'$column') AS redis_key,\
$column AS hkey1\
 FROM $src_tbl where date>='$curdate' and $column is not NULL\
 ) AS t1;\
"
echo "$mysql2redis"

} 
#and $column is not NULL\
#date>='$curdate'

#echo 'test'
#get_sql date
#mysql=$(get_sql date)
#echo $mysql

now="`date +%Y-%m-%d`"
#echo $now

curdate=$1
if [[ "" == $curdate ]]
then
    curdate=$now
fi

echo $curdate

#lcolumn=(cur date highest lowest opening volume turnover)
lcolumn=(cur date highest lowest opening )

allcmd=''
#for i in ${lcolumn[*]}
#do
   #cmd=$(get_sql $i $curdate)
   #echo $cmd #| mysql -h127.0.0.1 -uroot -p654321 -Dsat --skip-column-names --raw  | redis-cli --pipe 
   cmd=$(get_sql cur $curdate)
   cmd=$cmd
   cmd=$cmd$(get_sql date $curdate)
   cmd=$cmd$(get_sql highest $curdate)
   cmd=$cmd$(get_sql lowest $curdate)
   cmd=$cmd$(get_sql opening $curdate)
   cmd=$cmd$(get_sql volume $curdate)
   echo $cmd | mysql -h127.0.0.1 -uroot -p654321 -Dsat --skip-column-names --raw  | redis-cli --pipe 
   #allcmd=$allcmd$cmd
   #echo $allcmd
#done

#echo $allcmd | mysql -h127.0.0.1 -uroot -p654321 -Dsat --skip-column-names --raw  | redis-cli --pipe
 

##where code='000001' and date>='2014-11-25' 
##echo -en '*3\r\n$5\r\nlpush\r\n$9\r\n000001cur\r\n$2\r\n10\r\n' | redis-cli --pipe
## mysql -h127.0.0.1 -uroot -p654321 -Dsat --skip-column-names --raw < /home/lzw/code/my/sat/util/mysql2redis.sql | redis-cli --pipe
##cur,updown, updownrate, highest,lowest, closed,opening, volume, turnover, turnoverrate, outdisk, indisk,earningsrate,pb, amplitude,uplimit, #downlimit,buy1, sell1, date
#
