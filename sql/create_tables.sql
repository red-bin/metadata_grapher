CREATE TABLE sources (
  id SERIAL PRIMARY KEY,
  alias TEXT NOT NULL,
  url TEXT) ;

CREATE TABLE emails (
  id SERIAL PRIMARY KEY,
  source char(10)) ;

CREATE TABLE email_communications (
  id SERIAL PRIMARY KEY,
  email_id INT REFERENCES emails,
  sender_addr TEXT,
  sender_alias TEXT,
  recip_addr TEXT,
  recip_alias TEXT,
  comm_type TEXT NOT NULL,
  sent_time TIMESTAMP NOT NULL,
  received_time TIMESTAMP NOT NULL) ;
