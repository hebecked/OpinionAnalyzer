const logger = require("tracer").console();

exports.up = function(knex) {
  knex.schema.withSchema('news_meta_data').hasTable('analyzer_header').then(function(exists) {
    if(!exists) {
      return knex.schema.withSchema('news_meta_data').createTable("analyzer_header", function (table) {
        table.increments("id");
        table.string("analyzer_name",50).notNullable();
        table.string("analyzer_table_name",30).notNullable();
        table.string("analyzer_view_name",30).notNullable();
      });
    }
  })
    .then(function () {
      logger.log("Successfully created table analyzer_header!");
    });
};

exports.down = function(knex) {
  return knex.schema.dropTable("analyzer_header")
};
