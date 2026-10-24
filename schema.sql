CREATE TABLE CATEGORY (
    cat_id VARCHAR(10) PRIMARY KEY,
    cat_name VARCHAR(50) UNIQUE
);

CREATE TABLE EXPENSE (
    exp_id SERIAL PRIMARY KEY,
    date_time TIMESTAMP,
    amount DECIMAL(10,2),
    cat_id VARCHAR(10),
    FOREIGN KEY (cat_id) REFERENCES CATEGORY(cat_id)
);

CREATE TABLE BUDGET (
    bud_id INT PRIMARY KEY,
    bud_date DATE UNIQUE,
    bud_amount DECIMAL(10,2)
);