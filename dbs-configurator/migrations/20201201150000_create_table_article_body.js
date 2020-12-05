const logger = require("tracer").console();

exports.up = function(knex) {
  knex.schema.withSchema('news_meta_data').hasTable('article_body').then(function(exists) {
    if(!exists) {
      return knex.schema.withSchema('news_meta_data').createTable("article_body", function (table) {
        table.increments("id");
        table.integer("article_id").notNullable();
        table.string("headline",200).notNullable();
        table.text("body").notNullable();
        table.datetime("proc_timestamp").notNullable();
        table.integer("proc_counter").notNullable();
      });
    }
  })
    .then(function () {
      logger.log("Successfully created table article_body!");
    });
};

exports.down = function(knex) {
  return knex.schema.dropTable("article_body")
};
