const logger = require("tracer").console();

exports.up = function(knex) {
  knex.schema.withSchema('news_meta_data').hasTable('articles').then(function(exists) {
    if(!exists) {
      return knex.schema.withSchema('news_meta_data').createTable("articles", function (table) {
        table.increments("incremental_id");
        table.text("url");
        table.text("headline");
        table.date("published_at");
        table.timestamp("timestamp").defaultTo(knex.fn.now());
      });
    }
  })
    .then(function () {
      logger.log("Successfully created table articles!");
    });
};

exports.down = function(knex) {
  return knex.schema.dropTable("articles")
};
