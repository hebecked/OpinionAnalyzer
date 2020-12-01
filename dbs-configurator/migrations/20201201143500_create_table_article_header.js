const logger = require("tracer").console();

exports.up = function(knex) {
  return knex.schema.withSchema('news_meta_data').createTableIfNotExists("article_header", function (table) {
    table.increments("id");
    table.integer("source_id").notNullable();
    table.string("url",2048).notNullable();
    table.boolean("obsolete").notNullable();
    table.date("source_date");
  })
    .then(function () {
      logger.log("Successfully created metatables!");
    });
};

exports.down = function(knex) {
  return knex.schema.dropTable("test")
};
