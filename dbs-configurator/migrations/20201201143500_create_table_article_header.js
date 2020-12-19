const logger = require("tracer").console();

exports.up = function(knex) {
  knex.schema.withSchema('news_meta_data').hasTable('article_header').then(function(exists) {
    if(!exists) {
      return knex.schema.withSchema('news_meta_data').createTable("article_header", function (table) {
        table.increments("id");
        table.integer("source_id").notNullable();
        table.string("url",2048).notNullable();
        table.unique("url");
        table.boolean("obsolete").notNullable();
        table.date("source_date");
      });
    }
  })
    .then(function () {
      logger.log("Successfully created table article_header!");
    });
};

exports.down = function(knex) {
  return knex.schema.dropTable("article_header")
};
