insert into t_rt_price(code, cur,updown, updownrate, highest,lowest, closed,opening, volume, turnover, turnoverrate, outdisk, indisk,earningsrate,pb, amplitude,uplimit, downlimit,buy1, buy1volume, buy2,buy2volume, buy3, buy3volume, buy4, buy4volume, buy5, buy5volume,sell1, sell1volume,sell2,sell2volume,sell3, sell3volume, sell4,sell4volume,sell5,sell5volume,date,time) values(???)


create table t_rt_price(code char(6) not null, cur float(16,4),updown float(16,4), updownrate float(16,4), highest float(16,4),lowest float(16,4), closed float(16,4),opening float(16,4), volume float(16,4), turnover float(16,4), turnoverrate float(16,4), outdisk float(16,4), indisk float(16,4),earningsrate float(16,4),pb float(16,4), amplitude float(16,4),uplimit float(16,4), downlimit float(16,4),buy1 float(16,4), buy1volume float(16,4),buy2 float(16,4),buy2volume float(16,4), buy3 float(16,4), buy3volume float(16,4), buy4 float(16,4), buy4volume float(16,4), buy5 float(16,4), buy5volume float(16,4),sell1 float(16,4), sell1volume float(16,4),sell2 float(16,4),sell2volume float(16,4),sell3 float(16,4), sell3volume float(16,4), sell4 float(16,4),sell4volume float(16,4),sell5 float(16,4),sell5volume float(16,4),[date] DATE not NULL DEFAULT CURDATE() ,[time] TIME NOT NULL DEFAULT CURTIME(), primary key(code,date,time))

insert into t_rt_price(code,time) values('000002', NOW())

create table t_h_price(code char(6) not null, date DATE not NULL, time TIME not null, cur float(16,4), updown float(16,4), updownrate float(16,4), highest float(16,4),lowest float(16,4), closed float(16,4),opening float(16,4), volume decimal(20,4), turnover decimal(20,4), turnoverrate float(16,4), outdisk float(16,4), indisk float(16,4),earningsrate float(16,4),pb float(16,4), amplitude float(16,4),uplimit float(16,4), downlimit float(16,4),buy1 float(16,4),sell1 float(16,4), primary key(code,date,time) , unique INDEX t_h_price_code_date(code,date,time))

create index t_price_code_tradedate on t_price(code,tradedate);--ok
ALTER TABLE t_price ADD UNIQUE(code,tradedate);

# t_price历史数据转入t_h_price
INSERT t_h_price(code,date,cur) SELECT code,tradedate,Closingprice,Changes FROM t_price where code='000001.SZ' and tradedate ='2014-11-28';
INSERT t_h_price
(code,date,time,opening,highest,lowest,buy1,sell1,cur,updown,updownrate,volume,turnover,closed,turnoverrate,amplitude) 
SELECT
code,tradedate,tradedate,OpeningPrice, HighestPrice,LowestPrice,Bidprice,Offerprice,Closingprice,Changes, PriceChange, Volumes, Turnover, F002, F007, F008 FROM t_price where code='000001.SZ' and tradedate ='2014-11-28';

# t_h_sina to t_h_price
INSERT into t_h_price(code,date,time,cur,opening,highest,cur,lowest,volume) SELECT code,date,'000000',opening,highest,cur,lowest,volume FROM t_h_sina where date >='2014-12-06';


#t_rtprice 转入 t_h_price
insert t_h_price(code, cur,updown, updownrate, highest,lowest, closed,opening, volume, turnover, turnoverrate, outdisk, indisk,earningsrate,pb, amplitude,uplimit, downlimit,buy1, sell1, date,time) select code, cur,updown, updownrate, highest,lowest, closed,opening, volume, turnover, turnoverrate, outdisk, indisk,earningsrate,pb, amplitude,uplimit, downlimit,buy1, sell1, date,time from t_rt_price

updown,updownrate,highest,lowest,closed,opening,volume,turnover,turnoverrate,outdisk,indisk,earningsrate,pb,amplitude ,uplimit , downlimit ,

#add algo params table  default param: code=000000 algoname=...
create table t_algo_params(code char(6) not null, algoname varchar(20) not null, date DATE not NULL, pcount int(10), p1 float(16,4), p2 float(16,4), p3 float(16,4), p4 float(16,4), p5 float(16,4),  pstd float(16,4), pavg float(16,4), pMax float(16,4), pMin float(16,4), algoexplain varchar(255), primary key(code,algoname, date) , unique INDEX t_algo_params_code_algoname_date(code,algoname,date))

#example code='000000' is default params
INSERT into t_algo_params(code,algoname,date,pcount,p1) select '000000','wr',CURDATE(),'1','14'; 
INSERT into t_algo_params(code,algoname,date,pcount,p1,p2,p3) select '000000','kdj',CURDATE(),'3','9','3','3';
INSERT into t_algo_params(code,algoname,date,pcount,p1) select '000000','sar',CURDATE(),'1','4'; 

#trade
create table t_trade(code char(6) not null, date DATE not NULL, time TIME not null, price float(16,4), num float(16,0), money float(16,4), bsflag varchar(10), algo varchar(255) not null, primary key(code,date,time) , unique INDEX t_trade_code_date_time(code,date,time))
 
#mysql中的数据转入到redis
SELECT CONCAT(
"*4\r\n",
'$', LENGTH(redis_cmd), '\r\n',redis_cmd, '\r\n','$', LENGTH(redis_key), '\r\n',redis_key, '\r\n',
'$', LENGTH(hkey1), '\r\n',hkey1, '\r\n','$', LENGTH(hval1), '\r\n', hval1, '\r\n'
)
FROM (
 SELECT
'lpush' AS redis_cmd, CONCAT(code,'cur') AS redis_key,
'cur' AS hkey1,  'cur' AS hval1,
 FROM t_t_price where code='000001' and date='2014-11-28' 
 ) AS t

mysql -h 127.0.1 -uroot -p654321 -sat --skip-column-names --raw < /home/lzw/code/my/sat/util/redis.sql | redis-cli --pipe

1．ALTER TABLE

ALTER TABLE用来创建普通索引、UNIQUE索引或PRIMARY KEY索引。


ALTER TABLE table_name ADD INDEX index_name (column_list)

ALTER TABLE table_name ADD UNIQUE (column_list)

ALTER TABLE table_name ADD PRIMARY KEY (column_list)

 

其中table_name是要增加索引的表名，column_list指出对哪些列进行索引，多列时各列之间用逗号分隔。索引名index_name可选，缺省时，MySQL将根据第一个索引列赋一个名称。另外，ALTER TABLE允许在单个语句中更改多个表，因此可以在同时创建多个索引。
2．CREATE INDEX

CREATE INDEX可对表增加普通索引或UNIQUE索引。

 

CREATE INDEX index_name ON table_name (column_list)

CREATE UNIQUE INDEX index_name ON table_name (column_list)

 

table_name、index_name和column_list具有与ALTER TABLE语句中相同的含义，索引名不可选。另外，不能用CREATE INDEX语句创建PRIMARY KEY索引。
3．索引类型

在创建索引时，可以规定索引能否包含重复值。如果不包含，则索引应该创建为PRIMARY KEY或UNIQUE索引。对于单列惟一性索引，这保证单列不包含重复的值。对于多列惟一性索引，保证多个值的组合不重复。

PRIMARY KEY索引和UNIQUE索引非常类似。事实上，PRIMARY KEY索引仅是一个具有名称PRIMARY的UNIQUE索引。这表示一个表只能包含一个PRIMARY KEY，因为一个表中不可能具有两个同名的索引。

下面的SQL语句对students表在sid上添加PRIMARY KEY索引。

 

ALTER TABLE students ADD PRIMARY KEY (sid)
普通索引

这是最基本的索引，它没有任何限制，比如上文中为title字段创建的索引就是一个普通索引，MyIASM中默认的BTREE类型的索引，也是我们大多数情况下用到的索引。
01 	–直接创建索引
02 	CREATE INDEX index_name ON table(column(length))
03 	–修改表结构的方式添加索引
04 	ALTER TABLE table_name ADD INDEX index_name ON (column(length))
05 	–创建表的时候同时创建索引
06 	CREATE TABLE `table` (
07 	`id` int(11) NOT NULL AUTO_INCREMENT ,
08 	`title` char(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL ,
09 	`content` text CHARACTER SET utf8 COLLATE utf8_general_ci NULL ,
10 	`time` int(10) NULL DEFAULT NULL ,
11 	PRIMARY KEY (`id`),
12 	INDEX index_name (title(length))
13 	)
14 	–删除索引
15 	DROP INDEX index_name ON table

唯一索引

与普通索引类似，不同的就是：索引列的值必须唯一，但允许有空值（注意和主键不同）。如果是组合索引，则列值的组合必须唯一，创建方法和普通索引类似。
01 	–创建唯一索引
02 	CREATE UNIQUE INDEX indexName ON table(column(length))
03 	–修改表结构
04 	ALTER TABLE table_name ADD UNIQUE indexName ON (column(length))
05 	–创建表的时候直接指定
06 	CREATE TABLE `table` (
07 	`id` int(11) NOT NULL AUTO_INCREMENT ,
08 	`title` char(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL ,
09 	`content` text CHARACTER SET utf8 COLLATE utf8_general_ci NULL ,
10 	`time` int(10) NULL DEFAULT NULL ,
11 	PRIMARY KEY (`id`),
12 	UNIQUE indexName (title(length))
13 	);

全文索引（FULLTEXT）

MySQL从3.23.23版开始支持全文索引和全文检索，FULLTEXT索引仅可用于 MyISAM 表；他们可以从CHAR、VARCHAR或TEXT列中作为CREATE TABLE语句的一部分被创建，或是随后使用ALTER TABLE 或CREATE INDEX被添加。////对于较大的数据集，将你的资料输入一个没有FULLTEXT索引的表中，然后创建索引，其速度比把资料输入现有FULLTEXT索引的速度更为快。不过切记对于大容量的数据表，生成全文索引是一个非常消耗时间非常消耗硬盘空间的做法。
01 	–创建表的适合添加全文索引
02 	CREATE TABLE `table` (
03 	`id` int(11) NOT NULL AUTO_INCREMENT ,
04 	`title` char(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL ,
05 	`content` text CHARACTER SET utf8 COLLATE utf8_general_ci NULL ,
06 	`time` int(10) NULL DEFAULT NULL ,
07 	PRIMARY KEY (`id`),
08 	FULLTEXT (content)
09 	);
10 	–修改表结构添加全文索引
11 	ALTER TABLE article ADD FULLTEXT index_content(content)
12 	–直接创建索引
13 	CREATE FULLTEXT INDEX index_content ON article(content)

4. 单列索引、多列索引

多个单列索引与单个多列索引的查询效果不同，因为执行查询时，MySQL只能使用一个索引，会从多个索引中选择一个限制最为严格的索引。

5. 组合索引（最左前缀）

平时用的SQL查询语句一般都有比较多的限制条件，所以为了进一步榨取MySQL的效率，就要考虑建立组合索引。例如上表中针对title和time建立一个组合索引：ALTER TABLE article ADD INDEX index_titme_time (title(50),time(10))。建立这样的组合索引，其实是相当于分别建立了下面两组组合索引：

–title,time

–title

为什么没有time这样的组合索引呢？这是因为MySQL组合索引“最左前缀”的结果。简单的理解就是只从最左面的开始组合。并不是只要包含这两列的查询都会用到该组合索引，如下面的几个SQL所示：
1 	–使用到上面的索引
2 	SELECT * FROM article WHREE title='测试' AND time=1234567890;
3 	SELECT * FROM article WHREE utitle='测试';
4 	–不使用上面的索引
5 	SELECT * FROM article WHREE time=1234567890;
MySQL索引的优化

上面都在说使用索引的好处，但过多的使用索引将会造成滥用。因此索引也会有它的缺点：虽然索引大大提高了查询速度，同时却会降低更新表的速度，如对表进行INSERT、UPDATE和DELETE。因为更新表时，MySQL不仅要保存数据，还要保存一下索引文件。建立索引会占用磁盘空间的索引文件。一般情况这个问题不太严重，但如果你在一个大表上创建了多种组合索引，索引文件的会膨胀很快。索引只是提高效率的一个因素，如果你的MySQL有大数据量的表，就需要花时间研究建立最优秀的索引，或优化查询语句。下面是一些总结以及收藏的MySQL索引的注意事项和优化方法。



qtDict['updown'] = slist[1]
qtDict['updownrate'] = slist[1] 
qtDict['highest'] = slist[1]
qtDict['lowest'] = slist[1]
qtDict['closed'] = slist[1]
qtDict['opening'] = slist[1]
qtDict['volume'] = slist[1]
qtDict['turnover'] = slist[1]
qtDict['turnoverrate'] = slist[1]
qtDict['outdisk'] = slist[1]
qtDict['indisk'] = slist[1]
qtDict['earningsrate'] = slist[1]
qtDict['pb'] = slist[1] 
qtDict['amplitude'] = slist[1] 
qtDict['uplimit'] = slist[1] 
qtDict['downlimit'] = slist[1]
qtDict['buy1'] = slist[1]
qtDict['buy1volume'] = slist[1]
qtDict['buy2'] = slist[1]
qtDict['buy2volume'] = slist[1]
qtDict['buy3'] = slist[1]
qtDict['buy3volume'] = slist[1]
qtDict['buy4'] = slist[1]
qtDict['buy4volume'] = slist[1]
qtDict['buy5'] = slist[1]
qtDict['buy5volume'] = slist[1]
qtDict['sell1'] = slist[1]
qtDict['sell1volume'] = slist[1]
qtDict['sell2'] = slist[1]
qtDict['sell2volume'] = slist[1]
qtDict['sell3'] = slist[1]
qtDict['sell3volume'] = slist[1]
qtDict['sell4'] = slist[1]
qtDict['sell4volume'] = slist[1]
qtDict['sell5'] = slist[1]
qtDict['sell5volume'] = slist[1]


	qtDict['code'] = slist[2] # 代码，应该不需要包含sz,sh,hk
	qtDict['cur'] = (slist[3])     # 当前价格
	qtDict['closed'] = (slist[4]) #昨天收盘价
	qtDict['opening'] = (slist[5]) #开盘价
	qtDict['outdisk'] = (slist[7])
	qtDict['indisk'] = (slist[8]) 
	qtDict['buy1'] = (slist[9])
	qtDict['buy1volume'] = (slist[10])
	qtDict['buy2'] = (slist[11])
	qtDict['buy2volume'] = (slist[12])
	qtDict['buy3'] = (slist[13])
	qtDict['buy3volume'] = (slist[14])
	qtDict['buy4'] = (slist[15])
	qtDict['buy4volume'] = (slist[16])
	qtDict['buy5'] = (slist[17])
	qtDict['buy5volume'] =(slist[18])
	qtDict['sell1'] = (slist[19])
	qtDict['sell1volume'] = (slist[20])
	qtDict['sell2'] = (slist[21])
	qtDict['sell2volume'] =(slist[22])
	qtDict['sell3'] = (slist[23])
	qtDict['sell3volume'] = (slist[24])
	qtDict['sell4'] = (slist[25])
	qtDict['sell4volume'] =(slist[26])
	qtDict['sell5'] = (slist[27])
	qtDict['sell5volume'] =(slist[28])
	qtDict['time'] = slist[30]
	qtDict['updown'] = (slist[31]) #涨跌  
	qtDict['updownrate'] = (slist[32]) #涨跌幅% 
	qtDict['highest'] = (slist[33])
	qtDict['lowest'] = (slist[34])
	qtDict['tradeprice'] = slist[35]
	qtDict['tradevolume'] = slist[35]
	qtDict['tradeturnover'] = slist[35]
	qtDict['volume'] = (slist[36]) #总成交量
	qtDict['turnover'] = (slist[37]) #总成交额（万）
	qtDict['turnoverrate'] = (slist[38]) #换手率
	qtDict['earningsrate'] = slist[39]
	qtDict['amplitude'] = (slist[43])
	qtDict['pb'] = (slist[46])
	qtDict['uplimit'] = (slist[47])
	qtDict['downlimit'] = (slist[48])

#CREATE TABLE mytbl_new LIKE dbname.mytbl;
#INSERT mytbl_new SELECT * FROM dbname.mytbl;


insert ignore into t_h_price(code,date,time, cur,opening,highest,lowest,volume) 
select code,date,'000000',cur,opening,highest,lowest,volume from t_h_sina where code='000023' and date='2014-12-18';

insert ignore into t_h_price(code,date,time, cur,opening,highest,lowest,volume)
select code,date,'000000',cur,opening,highest,lowest,volume from t_h_yahoo where code='000023' and date='2014-12-18';

