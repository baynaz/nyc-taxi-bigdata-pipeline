CREATE TABLE Vendor (
    vendor_id INTEGER PRIMARY KEY,
    vendor_name VARCHAR(50)
);

-- Les arrondissements de New York
CREATE TABLE Borough (
    borough_id SERIAL PRIMARY KEY,
    borough_name VARCHAR(50) -- Ex: Manhattan, Queens
);

 -- Voir Taxi Zone Lookup Table (CSV)
CREATE TABLE Location_table (
    pulocation_id INTEGER PRIMARY KEY,
    zone_name VARCHAR(100),          -- Ex: Newark Airport
    service_zone VARCHAR(50),
    borough_id INTEGER REFERENCES Borough(borough_id)
);

CREATE TABLE Payment (
    payment_type_id INTEGER PRIMARY KEY,
    payment_name VARCHAR(50) -- Ex: Credit Card, Cash
);


CREATE TABLE RateCode (
    rate_code_id INTEGER PRIMARY KEY,
    rate_name VARCHAR(50) -- Ex: Standard, JFK
);


CREATE TABLE Trips (
    trip_id SERIAL PRIMARY KEY,
    
    -- Les clés étrangères
    vendor_id INTEGER REFERENCES Vendor(vendor_id),
    rate_code_id INTEGER REFERENCES RateCode(rate_code_id),
    payment_type_id INTEGER REFERENCES Payment(payment_type_id),
    pickup_location_id INTEGER REFERENCES Location_table(pulocation_id),
    dropoff_location_id INTEGER REFERENCES Location_table(pulocation_id),
    
    pickup_datetime TIMESTAMP,
    dropoff_datetime TIMESTAMP,
    
    -- Les Mesures
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
    airport_fee REAL
);