const fs = require('fs');
const logger = require("tracer").console();

const query = fs.readFileSync("/usr/src/app/sqlStorage/static_data/insert_static_data1.sql");

exports.up = function(knex) {
  return knex.schema.raw(query.toString())
      .then(function () {
      logger.log("Successfully inserted static data!");
    });
};

exports.down = function(knex) {
  return knex.schema.dropTable("test")
};
