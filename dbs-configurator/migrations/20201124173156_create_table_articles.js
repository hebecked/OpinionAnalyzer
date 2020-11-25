const logger = require("tracer").console();

exports.up = function(knex) {
  return knex.schema.withSchema('news_meta_data').createTableIfNotExists("articles", function (table) {
    table.increments("incremental_id");
    table.text("url");
    table.text("headline");
    table.date("published_at");
    table.timestamp("timestamp").defaultTo(knex.fn.now());
  })
    .then(function () {
      logger.log("Successfully created metatables!");
    });
};

exports.down = function(knex) {
  return knex.schema.dropTable("test")
};
