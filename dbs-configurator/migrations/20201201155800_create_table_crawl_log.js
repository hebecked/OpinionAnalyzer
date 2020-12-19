const logger = require("tracer").console();

exports.up = function(knex) {
  knex.schema.withSchema('news_meta_data').hasTable('crawl_log').then(function(exists) {
    if(!exists) {
      return knex.schema.withSchema('news_meta_data').createTable("crawl_log", function (table) {
        table.increments("id");
        table.integer("source_id").notNullable();
        table.timestamp("start_timestamp").notNullable();
        table.timestamp("end_timestamp");
        table.boolean("success").notNullable();
      });
    }
  })
    .then(function () {
      logger.log("Successfully created table crawl_log!");
    });
};

exports.down = function(knex) {
  return knex.schema.dropTable("crawl_log")
};
