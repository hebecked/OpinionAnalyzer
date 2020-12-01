const logger = require("tracer").console();

exports.up = function(knex) {
  return knex.schema.withSchema('news_meta_data').createTableIfNotExists("udf_values", function (table) {
    table.increments("id");
    table.integer("udf_id").notNullable();
    table.integer("object_type").notNullable();
    table.integer("object_id").notNullable();
    table.string("udf_value",80).notNullable();
  })
    .then(function () {
      logger.log("Successfully created metatables!");
    });
};

exports.down = function(knex) {
  return knex.schema.dropTable("test")
};
