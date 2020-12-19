const logger = require("tracer").console();

exports.up = function(knex) {
  knex.schema.withSchema('news_meta_data').hasTable('source_type_header').then(function(exists) {
    if(!exists) {
      return knex.schema.withSchema('news_meta_data').createTable("source_type_header", function (table) {
        table.increments("id");
        table.string("type",20).notNullable();
      });
    }
  })
    .then(function() {
      logger.log("Successfully created table source_type_header!");
    });
};

exports.down = function(knex) {
  return knex.schema.dropTable("source_type_header")
};
