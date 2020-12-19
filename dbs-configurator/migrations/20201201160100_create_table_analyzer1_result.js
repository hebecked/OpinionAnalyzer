const logger = require("tracer").console();

exports.up = function(knex) {
  knex.schema.withSchema('news_meta_data').hasTable('analyzer1_result').then(function(exists) {
    if(!exists) {
      return knex.schema.withSchema('news_meta_data').createTable("analyzer1_result", function (table) {
        table.increments("id");
        table.integer("comment_id").notNullable();
        table.integer("analyzer_log_id").notNullable();
        table.float("sentiment_value", { precision: 6, scale: 5 }).defaultTo(0.00000).notNullable();
        table.float("error_value", { precision: 6, scale: 5 }).defaultTo(0.00000).notNullable();
      });
    }
  })
    .then(function () {
      logger.log("Successfully created table analyzer1_result!");
    });
};

exports.down = function(knex) {
  return knex.schema.dropTable("analyzer1_result")
};
