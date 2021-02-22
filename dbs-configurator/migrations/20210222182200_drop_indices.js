const fs = require('fs');
const logger = require("tracer").console();

const query = fs.readFileSync("/usr/src/app/sqlStorage/indices/drop_index.sql");

exports.up = function(knex) {
  return knex.schema.raw(query.toString())
      .then(function () {
      logger.log("Successfully dropped indices!");
    });
};

exports.down = function(knex) {
  return knex.schema.dropTable("test")
};
