const fs = require('fs');
const logger = require("tracer").console();

const query = fs.readFileSync("/usr/src/app/sqlStorage/general_data/system_configuration.sql");

exports.up = function(knex) {
  return knex.schema.raw(query.toString())
      .then(function () {
      logger.log("Successfully created system_configuration table!");
    });
};

exports.down = function(knex) {
  return knex.schema.dropTable("general_data.system_configuration")
};
