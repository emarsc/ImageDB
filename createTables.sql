drop table if exists tag_links;
drop table if exists tags;
drop table if exists images;

create table images
(
	id bigint not null primary key auto_increment,
	source varchar(10) not null,
	url VARCHAR(2083),
	file_path VARCHAR(1000),
	source_id bigint,
	unique key(file_path),
	unique key(url),
	date_taken datetime,
	index (date_taken),
	date_retrieved timestamp default current_timestamp,
	gps POINT,
	latitude FLOAT(12, 9),
	longitude FLOAT (12, 9),
	useable int default 0,
	imagehash varchar (25) default null,
	downloaded int default 0,
	x_resolution int default null,
	y_resolution int default null,
	camera varchar(30) default null,
	notes varchar(500) default null
);


create table tags
(
	id bigint not null primary key auto_increment,
	tagname varchar(50) not null unique key
);

create table tag_links
(
	tag_id bigint not null,
	foreign key(tag_id) references tags(id),
	image_id bigint not null,
	foreign key(image_id) references images(id),
	primary key(tag_id, image_id),
	tag_value float(12, 9),
	tag_data json
);
