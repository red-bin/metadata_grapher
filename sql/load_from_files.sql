BEGIN ;
CREATE TEMP TABLE raw_houston (
  sender_addr TEXT,
  to_addr TEXT,
  CC text TEXT,
  BCC text TEXT,
  send_time text TEXT,
  receive_time TEXT)

COPY raw_houston (alias, url)
  FROM houston_metadata_path:
  WITH (FORMAT CSV, DELIMITER ',', NULL '', HEADER) ;
COMMIT ;
