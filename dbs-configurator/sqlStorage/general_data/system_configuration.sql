BEGIN;

CREATE TABLE IF NOT EXISTS general_data.system_configuration AS (
    SELECT
      'spiegel' AS news_type,
      true AS is_first_init

);

COMMIT;