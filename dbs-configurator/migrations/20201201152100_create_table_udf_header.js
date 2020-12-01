const logger = require("tracer").console();

exports.up = function(knex) {
  return knex.schema.withSchema('news_meta_data').createTableIfNotExists("udf_header", function (table) {
    table.increments("id");
    table.string("udf_name",30).notNullable();
  })
    .then(function () {
      logger.log("Successfully created metatables!");
    });
};

exports.down = function(knex) {
  return knex.schema.dropTable("test")
};
