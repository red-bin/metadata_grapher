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
  comm_type TEXT,
  sent_time TEXT,
  received_time TEXT) ;

CREATE TABLE departments (
  id SERIAL PRIMARY KEY,
  department_name TEXT ) ;

CREATE TABLE employees (
  id SERIAL PRIMARY KEY,
  first_name TEXT,
  mid_name TEXT,
  last_name TEXT,
  title TEXT,
  department_id INT REFERENCES departments,
  hire_date TIMESTAMP,
  status TEXT,
  base_pay_rate FLOAT,
  wage_type TEXT,
  email_address TEXT) ;

