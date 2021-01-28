const fs = require('fs');
const logger = require("tracer").console();

const query = fs.readFileSync("/usr/src/app/sqlStorage/grafana-user/grafana_user.sql");

exports.up = function(knex) {

  const GF_PG_USER = process.env.GF_PG_USER;
  const GF_PG_PASSWORD = process.env.GF_PG_PASSWORD;

  return knex.schema.raw(
      `CREATE USER ${GF_PG_USER} WITH PASSWORD '${GF_PG_PASSWORD}';
        REVOKE ALL PRIVILEGES ON DATABASE postgres FROM ${GF_PG_USER};
        GRANT USAGE ON SCHEMA news_meta_data TO ${GF_PG_USER};
        GRANT USAGE ON SCHEMA general_data TO ${GF_PG_USER};
        GRANT SELECT ON ALL TABLES IN SCHEMA news_meta_data TO ${GF_PG_USER};
        GRANT SELECT ON ALL TABLES IN SCHEMA general_data TO ${GF_PG_USER};`
  )
      .then(function () {
      logger.log("Successfully added grafana user with limited permissions!");
    });
};

exports.down = function(knex) {
  return knex.schema.dropTable("test")
};
