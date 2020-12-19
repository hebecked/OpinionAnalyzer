const fs = require('fs');
const logger = require("tracer").console();

const query = fs.readFileSync("/usr/src/app/sqlStorage/alter_tables/alter_tables.sql");

exports.up = function(knex) {
  return knex.schema.raw(query.toString())
      .then(function () {
      logger.log("Successfully added contraints!");
    });
};

exports.down = function(knex) {
  return knex.schema.dropTable("test")
};
