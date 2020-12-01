const logger = require("tracer").console();

exports.up = function(knex) {
  return knex.schema.withSchema('news_meta_data').createTableIfNotExists("crawl_log", function (table) {
    table.increments("id");
    table.integer("source_id").notNullable();
    table.timestamp("start_timestamp").notNullable();
    table.timestamp("end_timestamp");
    table.boolean("success").notNullable();
  })
    .then(function () {
      logger.log("Successfully created metatables!");
    });
};

exports.down = function(knex) {
  return knex.schema.dropTable("test")
};
