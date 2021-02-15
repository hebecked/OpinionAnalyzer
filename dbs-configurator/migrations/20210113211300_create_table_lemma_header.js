const logger = require("tracer").console();

exports.up = function(knex) {
  knex.schema.withSchema('news_meta_data').hasTable('lemma_header').then(function(exists) {
    if(!exists) {
      return knex.schema.withSchema('news_meta_data').createTable("lemma_header", function (table) {
        table.increments("id");
        table.string("lemma",30).notNullable();
	table.unique("lemma");
      });
    }
  })
    .then(function () {
      logger.log("Successfully created table lemma_header!");
    });
};

exports.down = function(knex) {
  return knex.schema.dropTable("lemma_header")
};
