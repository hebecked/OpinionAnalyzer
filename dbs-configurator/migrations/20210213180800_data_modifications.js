const fs = require('fs');
const logger = require("tracer").console();

const query = fs.readFileSync("/usr/src/app/sqlStorage/data_modifications/data_modifications.sql");

exports.up = function(knex) {
  return knex.schema.raw(query.toString())
      .then(function () {
      logger.log("Successfully modified data!");
    });
};

exports.down = function(knex) {
  return knex.schema.dropTable("test")
};
