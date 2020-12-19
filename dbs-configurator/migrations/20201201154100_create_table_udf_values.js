const logger = require("tracer").console();

exports.up = function(knex) {
  knex.schema.withSchema('news_meta_data').hasTable('udf_values').then(function(exists) {
    if(!exists) {
      return knex.schema.withSchema('news_meta_data').createTable("udf_values", function (table) {
        table.increments("id");
        table.integer("udf_id").notNullable();
        table.integer("object_type").notNullable();
        table.integer("object_id").notNullable();
        table.string("udf_value",80).notNullable();
        table.unique(["udf_id","object_type","object_id","udf_value"]);
      });
    }
  })
    .then(function () {
      logger.log("Successfully created table udf_values!");
    });
};

exports.down = function(knex) {
  return knex.schema.dropTable("udf_values")
};
