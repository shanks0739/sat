/**#/usr/local/mysql/data/sat/ipo.csv /home/lzw/code/my/myproject/indexdata_2014_11_28/ipo.csv**/

/*
create table t_ipo(code varchar(32) not null, startprice double(10,4), startdata datetime, primary key(code));
Transactionprice double(10,4),HighestPrice double(10,4),LowestPrice double(10,4),Bidprice double(10,4),Offerprice double(10,4),Closingprice double(10,4),Changes double(10,4),PriceChange double(10,4),Volumes decimal(20,4),Turnover decimal(20,4),TotalMarket decimal(20,4),Items double(10,4),EscrowShares double(10,4),CirculationShares double(10,4),Indate datetime,F001 double(10,4),F002 double(10,4),F003 double(10,4),F004 double(10,4),F005 varchar(255),F006 varchar(1024),F007 double(10,4),F008 double(10,4),

create table t_price(code varchar(32) not null, tradedate datetime, OpeningPrice double(10,4), Transactionprice double(10,4),HighestPrice double(10,4),LowestPrice double(10,4),Bidprice double(10,4),Offerprice double(10,4),Closingprice double(10,4),Changes double(10,4),PriceChange double(10,4),Volumes decimal(20,4),Turnover decimal(20,4),TotalMarket decimal(20,4),Items double(10,4),EscrowShares double(10,4),CirculationShares double(10,4),Indate datetime,xxxxxx varchar(255), F001 decimal(20,4),F002 double(10,4),F003 double(10,4),F004 double(10,4),F005 varchar(255),F006 varchar(1024),F007 double(10,4),F008 double(10,4), primary key(code,tradedate));

*/


load data infile '/usr/local/mysql/data/sat/001070020.csv.b'
into table t_price fields terminated by ','  optionally enclosed by '"' escaped by '"'   lines terminated by '\r\n';

load data infile '/usr/local/mysql/data/sat/001070030.csv.b'
into table t_price fields terminated by ','  optionally enclosed by '"' escaped by '"'   lines terminated by '\r\n';

load data infile '/usr/local/mysql/data/sat/001070040.csv.b'
into table t_price fields terminated by ','  optionally enclosed by '"' escaped by '"'   lines terminated by '\r\n';

load data infile '/usr/local/mysql/data/sat/001070050.csv.b'
into table t_price fields terminated by ','  optionally enclosed by '"' escaped by '"'   lines terminated by '\r\n';

load data infile '/usr/local/mysql/data/sat/001070060.csv.b'
into table t_price fields terminated by ','  optionally enclosed by '"' escaped by '"'   lines terminated by '\r\n';

load data infile '/usr/local/mysql/data/sat/001070070.csv.b'
into table t_price fields terminated by ','  optionally enclosed by '"' escaped by '"'   lines terminated by '\r\n';

load data infile '/usr/local/mysql/data/sat/001070080.csv.b'
into table t_price fields terminated by ','  optionally enclosed by '"' escaped by '"'   lines terminated by '\r\n';

load data infile '/usr/local/mysql/data/sat/001070090.csv.b'
into table t_price fields terminated by ','  optionally enclosed by '"' escaped by '"'   lines terminated by '\r\n';

load data infile '/usr/local/mysql/data/sat/001070100.csv.b'
into table t_price fields terminated by ','  optionally enclosed by '"' escaped by '"'   lines terminated by '\r\n';

load data infile '/usr/local/mysql/data/sat/001070110.csv.b'
into table t_price fields terminated by ','  optionally enclosed by '"' escaped by '"'   lines terminated by '\r\n';

load data infile '/usr/local/mysql/data/sat/001070120.csv.b'
into table t_price fields terminated by ','  optionally enclosed by '"' escaped by '"'   lines terminated by '\r\n';

load data infile '/usr/local/mysql/data/sat/001070130.csv.b'
into table t_price fields terminated by ','  optionally enclosed by '"' escaped by '"'   lines terminated by '\r\n';

load data infile '/usr/local/mysql/data/sat/001070140.csv.b'
into table t_price fields terminated by ','  optionally enclosed by '"' escaped by '"'   lines terminated by '\r\n';

load data infile '/usr/local/mysql/data/sat/001070150.csv.b'
into table t_price fields terminated by ','  optionally enclosed by '"' escaped by '"'   lines terminated by '\r\n';

load data infile '/usr/local/mysql/data/sat/001070160.csv.b'
into table t_price fields terminated by ','  optionally enclosed by '"' escaped by '"'   lines terminated by '\r\n';

load data infile '/usr/local/mysql/data/sat/001070170.csv.b'
into table t_price fields terminated by ','  optionally enclosed by '"' escaped by '"'   lines terminated by '\r\n';

load data infile '/usr/local/mysql/data/sat/001070180.csv.b'
into table t_price fields terminated by ','  optionally enclosed by '"' escaped by '"'   lines terminated by '\r\n';

load data infile '/usr/local/mysql/data/sat/001070190.csv.b'
into table t_price fields terminated by ','  optionally enclosed by '"' escaped by '"'   lines terminated by '\r\n';



   
