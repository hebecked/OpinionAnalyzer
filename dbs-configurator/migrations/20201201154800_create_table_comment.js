const logger = require("tracer").console();

exports.up = function(knex) {
  knex.schema.withSchema('news_meta_data').hasTable('comment').then(function(exists) {
    if(!exists) {
      return knex.schema.withSchema('news_meta_data').createTable("comment", function (table) {
        table.increments("id");
        table.biginteger("external_id").notNullable();
        table.integer("article_body_id").notNullable();
        table.unique(["external_id","article_body_id"]);
        table.biginteger("parent_id");
        table.integer("level").notNullable();
        table.text("body").notNullable();
        table.timestamp("proc_timestamp").notNullable();
      });
    }
  })
    .then(function () {
      logger.log("Successfully created table comment!");
    });
};

exports.down = function(knex) {
  return knex.schema.dropTable("comment")
};
