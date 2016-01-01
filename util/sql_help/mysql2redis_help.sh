!/bin/bash

mysql_host=127.0.0.1
mysql_user=root
mysql_pwd=654321 
database=sat
tbls_prefix="test_tbl_name_prefix"

#调用shell时，传入的日期参数
cur_dt="$1"  
#遍历表，返回表名list
table_list=$(mysql -h$mysql_host -u$mysql_user -p$mysql_pwd $database -A -Bse "show tables") 

code, cur,updown, updownrate, highest,lowest, closed,opening, volume, turnover, turnoverrate, outdisk, indisk,earningsrate,pb, amplitude,uplimit, downlimit,buy1, sell1, date
function gen_sql()
{
  src_tbl=$1
  mysql2redis="SELECT CONCAT(\
    '*21\r\n',\
    '$', LENGTH(redis_cmd), '\r\n',redis_cmd, '\r\n',\
    '$', LENGTH(redis_key), '\r\n',redis_key, '\r\n',\
    '$', LENGTH(hkey1), '\r\n', hkey1, '\r\n',\
    '$', LENGTH(hval1), '\r\n', hval1, '\r\n',\
    '$', LENGTH(hkey2), '\r\n', hkey2, '\r\n',\
    '$', LENGTH(hval2), '\r\n', hval2, '\r\n',\
    '$', LENGTH(hkey3), '\r\n', hkey3, '\r\n',\
    '$', LENGTH(hval3), '\r\n', hval3, '\r\n',\
    '$', LENGTH(hkey4), '\r\n', hkey4, '\r\n',\
    '$', LENGTH(hval4), '\r\n', hval4, '\r'\
  )\
  FROM (\
    SELECT\
    'HMSET' AS redis_cmd, uniq_id AS redis_key,\
    'f1' AS hkey1, f1 AS hval1,\
    'f2' AS hkey2, f2 AS hval2,\
    'f3' AS hkey3, f3 AS hval3,\
    'f4' AS hkey4, f4 AS hval4\
    FROM $src_tbl WHERE dt='$cur_dt'\
  ) AS T"
  echo "$mysql2redis"
}

prefix_len=$(expr length $tbls_prefix)
for arg in $table_list
do
  if [[ "${arg:0:$prefix_len}" == ${tbls_prefix} ]] # 判断表名是否匹配(表名以指定前缀开头)
  then
    mysql2redisCmd=$(gen_sql $arg)
    echo $mysql2redisCmd | mysql -u$mysql_user -p$mysql_pwd -h$mysql_host $database --skip-column-names --raw | redis-cli -n 1 --pipe
  fi                                                                                                                                      done

