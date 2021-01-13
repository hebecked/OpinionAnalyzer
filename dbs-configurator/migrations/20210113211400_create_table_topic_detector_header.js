const logger = require("tracer").console();

exports.up = function(knex) {
  knex.schema.withSchema('news_meta_data').hasTable('topic_detector_header').then(function(exists) {
    if(!exists) {
      return knex.schema.withSchema('news_meta_data').createTable("topic_detector_header", function (table) {
        table.increments("id");
        table.string("topic_detector",30).notNullable();
	table.unique("topic_detector");
      });
    }
  })
    .then(function () {
      logger.log("Successfully created table topic_detector_header!");
    });
};

exports.down = function(knex) {
  return knex.schema.dropTable("topic_detector_header")
};
