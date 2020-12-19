const logger = require("tracer").console();

exports.up = function(knex) {
  knex.schema.withSchema('news_meta_data').hasTable('object_header').then(function(exists) {
    if(!exists) {
      return knex.schema.withSchema('news_meta_data').createTable("object_header", function (table) {
        table.increments("id");
        table.string("type",20).notNullable();
      });
    }
  })
    .then(function () {
      logger.log("Successfully created table object_header!");
    });
};

exports.down = function(knex) {
  return knex.schema.dropTable("object_header")
};
