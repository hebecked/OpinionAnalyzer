const logger = require("tracer").console();

exports.up = function(knex) {
  return knex.schema.withSchema('news_meta_data').createTableIfNotExists("comment", function (table) {
    table.increments("id");
    table.integer("article_body_id").notNullable();
    table.integer("parent_id");
    table.integer("level").notNullable();
    table.text("body").notNullable();
    table.timestamp("proc_timestamp").notNullable();
    table.integer("proc_counter").notNullable();
  })
    .then(function () {
      logger.log("Successfully created metatables!");
    });
};

exports.down = function(knex) {
  return knex.schema.dropTable("test")
};
