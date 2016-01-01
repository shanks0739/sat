#!/bin/bash

# t_rt_price to t_h_price 

now="`date +%Y-%m-%d`"
#echo $now

curdate=$1
if [[ "" == $curdate ]]
then
    curdate=$now
fi

echo $curdate

showTables='show tables;'

echo "load realtime  data to history start"
mysql -uroot -p654321 << EOF
use sat;

insert ignore t_h_price(code, cur,updown, updownrate, highest,lowest, closed,opening, volume, turnover, turnoverrate, outdisk, indisk,earningsrate,pb, amplitude,uplimit, downlimit,buy1, sell1, date,time) select code, cur,updown, updownrate, highest,lowest, closed,opening, volume, turnover, turnoverrate, outdisk, indisk,earningsrate,pb, amplitude,uplimit, downlimit,buy1, sell1, date,'000000' from t_rt_price where date >= '$curdate' and time>='15:00:00';

EOF

#cat << EOF
# '$curdate'
#EOF

echo "load realtime data to history end"

