const logger = require("tracer").console();

exports.up = function(knex) {
  knex.schema.withSchema('news_meta_data').hasTable('analyzer_log').then(function(exists) {
    if(!exists) {
      return knex.schema.withSchema('news_meta_data').createTable("analyzer_log", function (table) {
        table.increments("id");
        table.integer("comment_id").notNullable();
        table.integer("analyzer_id").notNullable();
        table.timestamp("start_timestamp");
        table.timestamp("end_timestamp");
        table.boolean("success").defaultTo(false).notNullable();
      });
    }
  })
    .then(function () {
      logger.log("Successfully created table analyzer_log!");
    });
};

exports.down = function(knex) {
  return knex.schema.dropTable("analyzer_log")
};
