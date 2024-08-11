CREATE TABLE IF NOT EXISTS fraud_data (
    transaction_id SERIAL PRIMARY KEY,
    trans_date_trans_time TIMESTAMP,
    merchant VARCHAR(255),
    category VARCHAR(50),
    amt NUMERIC,
    city VARCHAR(100),
    state VARCHAR(10),
    lat NUMERIC,
    long NUMERIC,
    city_pop INTEGER,
    job VARCHAR(255),
    dob DATE,
    trans_num VARCHAR(50),
    merch_lat NUMERIC,
    merch_long NUMERIC,
    is_fraud BOOLEAN
);



CREATE TABLE IF NOT EXISTS merchants (
    merchant_id SERIAL PRIMARY KEY,
    merchant_name VARCHAR(255),
    category VARCHAR(50)
);



CREATE TABLE IF NOT EXISTS locations (
    location_id SERIAL PRIMARY KEY,
    city VARCHAR(100),
    state VARCHAR(10),
    lat NUMERIC,
    long NUMERIC,
    city_pop INTEGER
);



CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    job VARCHAR(255),
    dob DATE
);



ALTER TABLE fraud_data
ADD COLUMN merchant_id INT REFERENCES merchants(merchant_id),
ADD COLUMN location_id INT REFERENCES locations(location_id),
ADD COLUMN user_id INT REFERENCES users(user_id);

INSERT INTO merchants (merchant_name, category)
SELECT DISTINCT merchant, category FROM fraud_data;


INSERT INTO locations (city, state, lat, long, city_pop)
SELECT DISTINCT city, state, lat, long, city_pop FROM fraud_data;


INSERT INTO users (job, dob)
SELECT DISTINCT job, dob FROM fraud_data;


UPDATE fraud_data
SET merchant_id = m.merchant_id
FROM merchants m
WHERE fraud_data.merchant = m.merchant_name AND fraud_data.category = m.category;


UPDATE fraud_data
SET location_id = l.location_id
FROM locations l
WHERE fraud_data.city = l.city AND fraud_data.state = l.state 
AND fraud_data.lat = l.lat AND fraud_data.long = l.long;



UPDATE fraud_data
SET user_id = u.user_id
FROM users u
WHERE fraud_data.job = u.job AND fraud_data.dob = u.dob;


ALTER TABLE fraud_data
DROP COLUMN merchant,
DROP COLUMN category,
DROP COLUMN city,
DROP COLUMN state,
DROP COLUMN lat,
DROP COLUMN long,
DROP COLUMN city_pop,
DROP COLUMN job,
DROP COLUMN dob;



CREATE INDEX idx_trans_date ON fraud_data (trans_date_trans_time);
CREATE INDEX idx_merchant_id ON fraud_data (merchant_id);
CREATE INDEX idx_location_id ON fraud_data (location_id);
CREATE INDEX idx_user_id ON fraud_data (user_id);
CREATE INDEX idx_is_fraud ON fraud_data (is_fraud);


CREATE TABLE IF NOT EXISTS states (
    state_abbr VARCHAR(2) PRIMARY KEY,
    state_name VARCHAR(50)
);


CREATE TABLE IF NOT EXISTS states (
    state_abbr VARCHAR(2) PRIMARY KEY,
    state_name VARCHAR(50)
);

DELETE FROM states;


INSERT INTO states (state_abbr, state_name) VALUES
('AK', 'Alaska'),
('MO', 'Missouri'),
('NE', 'Nebraska'),
('CA', 'California'),
('UT', 'Utah'),
('OR', 'Oregon'),
('WY', 'Wyoming'),
('NM', 'New Mexico'),
('AZ', 'Arizona'),
('WA', 'Washington'),
('CO', 'Colorado'),
('ID', 'Idaho'),
('HI', 'Hawaii')
ON CONFLICT (state_abbr) DO NOTHING;


SELECT EXTRACT(YEAR FROM trans_date_trans_time) AS Year, COUNT(*) AS Transactions
FROM fraud_data
GROUP BY EXTRACT(YEAR FROM trans_date_trans_time);
