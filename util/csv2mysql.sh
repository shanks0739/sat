#!/bin/bash

#load data infile '/tmp/file.csv' into table _tablename (set character# utf8)
#fields terminated by ','
#enclosed by '"'
#lines terminated by '\r\n'; 

echo "load csv data to mysql start"
mysql -uroot -p654321 << EOF
use sat;
load data infile '/usr/local/mysql/data/sat/his_sina.csv' REPLACE into table t_h_sina  fields terminated by ','  lines terminated by '\n';

insert ignore into t_h_price(code,date,time, cur,opening,highest,lowest,volume)  select code,date,'000000',cur,opening,highest,lowest,volume from t_h_sina where date>='2000-01-01';

EOF

echo "load csv data to mysql end"

#sudo mysql -uroot -p654321 < csv2mysql.sql

