const logger = require("tracer").console();

exports.up = function(knex) {
  knex.schema.withSchema('news_meta_data').hasTable('topic_detector_result').then(function(exists) {
    if(!exists) {
      return knex.schema.withSchema('news_meta_data').createTable("topic_detector_result", function (table) {
        table.increments("id");
        table.integer("article_header_id").defaultTo(0).notNullable();
        table.integer("topic_detector_id").defaultTo(0).notNullable();
        table.integer("lemma_id").defaultTo(0).notNullable();	
	table.date("run_date").notNullable();
	table.unique(["article_header_id","topic_detector_id","lemma_id","run_date"]);
      });
    }
  })
    .then(function () {
      logger.log("Successfully created table topic_detector_result!");
    });
};

exports.down = function(knex) {
  return knex.schema.dropTable("topic_detector_result")
};
