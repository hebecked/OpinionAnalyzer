const logger = require("tracer").console();

exports.up = function(knex) {
  knex.schema.withSchema('news_meta_data').hasTable('udf_header').then(function(exists) {
    if(!exists) {
      return knex.schema.withSchema('news_meta_data').createTable("udf_header", function (table) {
        table.increments("id");
        table.string("udf_name",30).notNullable();
      });
    }
  })
    .then(function () {
      logger.log("Successfully created table udf_header!");
    });
};

exports.down = function(knex) {
  return knex.schema.dropTable("udf_header")
};
