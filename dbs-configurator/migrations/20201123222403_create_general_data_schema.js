const logger = require("tracer").console();

exports.up = function(knex) {
  return knex.schema.raw(
      'CREATE SCHEMA IF NOT EXISTS general_data'
  )
      .then(function () {
      logger.log("Successfully created general_data schema!");
    });
};

exports.down = function(knex) {
  return knex.schema.dropSchema("general_data")
};
