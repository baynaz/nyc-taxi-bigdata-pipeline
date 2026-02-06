-- Only execute the block of DROP TABLE lines of code when needed
/*
DROP TABLE IF EXISTS Trips CASCADE;
DROP TABLE IF EXISTS Location_table CASCADE;
DROP TABLE IF EXISTS Borough CASCADE;
DROP TABLE IF EXISTS Vendor CASCADE;
DROP TABLE IF EXISTS Payment CASCADE;
DROP TABLE IF EXISTS RateCode CASCADE;
DROP TABLE IF EXISTS TimeDimension CASCADE;
*/

CREATE TABLE IF NOT EXISTS Vendor (
    vendor_id INTEGER PRIMARY KEY,
    vendor_name VARCHAR(50)
);

-- Les arrondissements de New York
CREATE TABLE IF NOT EXISTS Borough (
    borough_id SERIAL PRIMARY KEY,
    borough_name VARCHAR(50) -- Ex: Manhattan, Queens
);

 -- Voir Taxi Zone Lookup Table (CSV)
CREATE TABLE IF NOT EXISTS Location_table (
    pulocation_id INTEGER PRIMARY KEY,
    zone_name VARCHAR(100),          -- Ex: Newark Airport
    service_zone VARCHAR(50),
    borough_id INTEGER REFERENCES Borough(borough_id)
);

CREATE TABLE IF NOT EXISTS Payment (
    payment_type_id INTEGER PRIMARY KEY,
    payment_name VARCHAR(50) -- Ex: Credit Card, Cash
);


CREATE TABLE IF NOT EXISTS RateCode (
    rate_code_id INTEGER PRIMARY KEY,
    rate_name VARCHAR(50) -- Ex: Standard, JFK
);

CREATE TABLE IF NOT EXISTS TimeDimension (
                                             time_id SERIAL PRIMARY KEY,
                                             year INT NOT NULL,
                                             month INT NOT NULL,
                                             month_name VARCHAR(20),
                                             year_month VARCHAR(7) UNIQUE
);

CREATE TABLE IF NOT EXISTS Trips (
     trip_id SERIAL PRIMARY KEY,

     vendor_id INTEGER REFERENCES Vendor(vendor_id),
     rate_code_id INTEGER REFERENCES RateCode(rate_code_id),
     payment_type_id INTEGER REFERENCES Payment(payment_type_id),
     pickup_location_id INTEGER REFERENCES Location_table(pulocation_id),
     dropoff_location_id INTEGER REFERENCES Location_table(pulocation_id),

     pickup_datetime TIMESTAMP,
     dropoff_datetime TIMESTAMP,

     time_id INT REFERENCES TimeDimension(time_id),

     passenger_count INTEGER,
     trip_distance REAL,
     fare_amount REAL,
     extra REAL,
     mta_tax REAL,
     tip_amount REAL,
     tolls_amount REAL,
     improvement_surcharge REAL,
     total_amount REAL,
     congestion_surcharge REAL,
     airport_fee REAL,

     month VARCHAR(7)
);

