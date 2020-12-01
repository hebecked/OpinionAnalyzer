const logger = require("tracer").console();

exports.up = function(knex,Promise) {
  return knex.schema.withSchema('news_meta_data').createTableIfNotExists("source_type_header", function (table) {
logger.log("1");
    table.increments("id");
    table.string("type",20).notNullable();
  })
    .then(function() {
      logger.log("Successfully created metatables!");
    });
};

exports.down = function(knex) {
  return knex.schema.dropTable("test")
};
