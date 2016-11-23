--CREATE KEYSPACE dmp with REPLICATION ={'class':'SimpleStrategy', 'replication_factor':2 };
CREATE KEYSPACE dmp WITH REPLICATION = {'class' : 'NetworkTopologyStrategy', 'dcnode7' : 2};

CREATE TABLE dmp.user_tags (
  user_id text,
  tag_id int,
  log_time bigint,
  primary key (user_id, tag_id)
)
;

CREATE INDEX idx_user_tags ON dmp.user_tags (log_time);

CREATE TABLE dmp.tag_users (
  source_id int,
  tag_id int,
  user_id text,
  log_time bigint,
  primary key ((source_id, tag_id), user_id)
)
;

CREATE TABLE dmp.tags (
  tag_id int,
  tag_name text,
  tag_group_id int,
  tag_group_name text,
  tag_property_id int,
  tag_property_name text,
  primary key (tag_id)
)
;