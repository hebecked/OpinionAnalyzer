const fs = require('fs');
const logger = require("tracer").console();

const query = fs.readFileSync("/usr/src/app/sqlStorage/stored_procedures/create_procedure2.sql");

exports.up = function(knex) {
  return knex.schema.raw(query.toString())
      .then(function () {
      logger.log("Successfully created stored procedures!");
    });
};

exports.down = function(knex) {
  return knex.schema.dropTable("test")
};
