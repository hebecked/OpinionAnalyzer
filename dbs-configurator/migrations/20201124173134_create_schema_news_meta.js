const logger = require("tracer").console();

exports.up = function(knex) {
  return knex.schema.raw(
      'CREATE SCHEMA IF NOT EXISTS news_meta_data'
  )
      .then(function () {
      logger.log("Successfully created news_meta_data schema!");
    });
};

exports.down = function(knex) {
  return knex.schema.dropSchema("news_meta_data")
};
