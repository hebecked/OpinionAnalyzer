const logger = require("tracer").console();

exports.up = function(knex) {
  knex.schema.withSchema('news_meta_data').hasTable('lemma_count').then(function(exists) {
    if(!exists) {
      return knex.schema.withSchema('news_meta_data').createTable("lemma_count", function (table) {
        table.increments("id");
        table.integer("lemma_id").notNullable();
        table.integer("article_body_id").notNullable();
        table.integer("lemma_count").defaultTo(0).notNullable();
	table.unique(["lemma_id","article_body_id"]);
      });
    }
  })
    .then(function () {
      logger.log("Successfully created table lemma_count!");
    });
};

exports.down = function(knex) {
  return knex.schema.dropTable("lemma_count")
};
