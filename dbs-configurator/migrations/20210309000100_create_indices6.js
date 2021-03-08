const fs = require('fs');
const logger = require("tracer").console();

const query = fs.readFileSync("/usr/src/app/sqlStorage/indices/create_index6.sql");

exports.up = function(knex) {
  return knex.schema.raw(query.toString())
      .then(function () {
      logger.log("Successfully created indices!");
    });
};

exports.down = function(knex) {
  return knex.schema.dropTable("test")
};
