const logger = require("tracer").console();

exports.up = function(knex) {
  knex.schema.withSchema('news_meta_data').hasTable('source_header').then(function(exists) {
    if(!exists) {
      return knex.schema.withSchema('news_meta_data').createTable("source_header", function (table) {
        table.increments("id");
        table.integer("type").notNullable();
        table.string("source",80).notNullable();
      });
    }
  })
    .then(function () {
      logger.log("Successfully created table source_header!");
    });
};

exports.down = function(knex) {
  return knex.schema.dropTable("source_header")
};
