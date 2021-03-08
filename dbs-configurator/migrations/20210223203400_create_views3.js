const fs = require('fs');
const logger = require("tracer").console();

const query = fs.readFileSync("/usr/src/app/sqlStorage/views/create_views3.sql");

exports.up = function(knex) {
  return knex.schema.raw(query.toString())
      .then(function () {
      logger.log("Successfully created views!");
    });
};

exports.down = function(knex) {
  return knex.schema.dropTable("test")
};
