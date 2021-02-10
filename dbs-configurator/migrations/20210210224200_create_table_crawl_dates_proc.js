const logger = require("tracer").console();

exports.up = function(knex) {
  knex.schema.withSchema('news_meta_data').hasTable('crawl_dates_proc').then(function(exists) {
    if(!exists) {
      return knex.schema.withSchema('news_meta_data').createTable("crawl_dates_proc", function (table) {
        table.increments("id");
        table.integer("source_id").defaultTo(0).notNullable();
	table.date("date_processed").notNullable();
      });
    }
  })
    .then(function () {
      logger.log("Successfully created table crawl_dates_proc!");
    });
};

exports.down = function(knex) {
  return knex.schema.dropTable("crawl_dates_proc")
};
