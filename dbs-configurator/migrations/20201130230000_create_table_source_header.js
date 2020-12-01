const logger = require("tracer").console();

exports.up = function(knex) {
  return knex.schema.withSchema('news_meta_data').createTableIfNotExists("source_header", function (table) {
    table.increments("id");
    table.integer("type").notNullable();
    table.string("source",80).notNullable();
  })
    .then(function () {
      logger.log("Successfully created metatables!");
    });
};

exports.down = function(knex) {
  return knex.schema.dropTable("test")
};
