const logger = require("tracer").console();

exports.up = function(knex) {
  knex.schema.withSchema('news_meta_data').hasTable('doc_count').then(function(exists) {
    if(!exists) {
      return knex.schema.withSchema('news_meta_data').createTable("doc_count", function (table) {
        table.increments("id");
        table.integer("lemma_id").notNullable();
        table.integer("doc_count").defaultTo(0).notNullable();
	table.date("mth_published").notNullable();
	table.unique(["lemma_id","mth_published"]);
      });
    }
  })
    .then(function () {
      logger.log("Successfully created table doc_count!");
    });
};

exports.down = function(knex) {
  return knex.schema.dropTable("doc_count")
};
