const fs = require('fs');
const logger = require("tracer").console();

const query = fs.readFileSync("/usr/src/app/sqlStorage/drop_tables/drop_tables.sql");

exports.up = function(knex) {
  return knex.schema.raw(query.toString())
      .then(function () {
      logger.log("Successfully dropped tables!");
    });
};

exports.down = function(knex) {
  return knex.schema.dropTable("test")
};
