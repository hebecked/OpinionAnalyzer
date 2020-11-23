BEGIN;

CREATE TABLE IF NOT EXISTS general_data.date_time_dimension AS (
    SELECT
        datum AS date,
        TO_CHAR(datum, 'Day') AS day_name,
        EXTRACT(ISODOW FROM datum) AS day_of_week,
        EXTRACT(DAY FROM datum) AS day_of_month,
        datum - DATE_TRUNC('quarter', datum)::DATE + 1 AS day_of_quarter,
        EXTRACT(DOY FROM datum) AS day_of_year,
        TO_CHAR(datum, 'W')::INT AS week_of_month,
        EXTRACT(WEEK FROM datum) AS week_of_year,
        EXTRACT(MONTH FROM datum) AS month_actual,
        TO_CHAR(datum, 'Month') AS month_name,
        TO_CHAR(datum, 'Mon') AS month_name_abbreviated,
        EXTRACT(QUARTER FROM datum) AS quarter_actual,
        CASE
           WHEN EXTRACT(QUARTER FROM datum) = 1 THEN 'First'
           WHEN EXTRACT(QUARTER FROM datum) = 2 THEN 'Second'
           WHEN EXTRACT(QUARTER FROM datum) = 3 THEN 'Third'
           WHEN EXTRACT(QUARTER FROM datum) = 4 THEN 'Fourth'
        END AS quarter_name,
        EXTRACT(ISOYEAR FROM datum) AS year_actual,
        datum + (1 - EXTRACT(ISODOW FROM datum))::INT AS first_day_of_week,
        datum + (7 - EXTRACT(ISODOW FROM datum))::INT AS last_day_of_week,
        datum + (1 - EXTRACT(DAY FROM datum))::INT AS first_day_of_month,
        (DATE_TRUNC('MONTH', datum) + INTERVAL '1 MONTH - 1 day')::DATE AS last_day_of_month,
        DATE_TRUNC('quarter', datum)::DATE AS first_day_of_quarter,
        (DATE_TRUNC('quarter', datum) + INTERVAL '3 MONTH - 1 day')::DATE AS last_day_of_quarter,
        TO_DATE(EXTRACT(YEAR FROM datum) || '-01-01', 'YYYY-MM-DD') AS first_day_of_year,
        TO_DATE(EXTRACT(YEAR FROM datum) || '-12-31', 'YYYY-MM-DD') AS last_day_of_year,
        TO_CHAR(datum, 'mmyyyy') AS mmyyyy,
        TO_CHAR(datum, 'mmddyyyy') AS mmddyyyy,
        CASE
           WHEN EXTRACT(ISODOW FROM datum) IN (6, 7) THEN TRUE
           ELSE FALSE
        END AS weekend_indr
    FROM
        (
        SELECT
            '1970-01-01'::DATE + SEQUENCE.DAY AS datum
        FROM
            GENERATE_SERIES(0, 29219) AS SEQUENCE (DAY)
        GROUP BY
            SEQUENCE.DAY
        ) DQ
);

ALTER TABLE general_data.date_time_dimension ADD CONSTRAINT d_date_time_dim_id_pk PRIMARY KEY (date);

CREATE INDEX d_date_time_dim_date_actual_idx ON general_data.date_time_dimension(date);

COMMIT;
