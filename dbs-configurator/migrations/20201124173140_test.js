const logger = require("tracer").console();

exports.up = function(knex) {
  knex.schema.withSchema('news_meta_data').hasTable('test').then(function(exists) {
    if(!exists) {
      return knex.schema.withSchema('news_meta_data').createTable("test", function (table) {
        table.timestamp("timestamp").defaultTo(knex.fn.now());
        table.integer("testXY").nullable();
        table.primary("timestamp");
      });
    }
  })
    .then(function () {
      logger.log("Successfully created table test!");
    });
};

exports.down = function(knex) {
  return knex.schema.dropTable("test")
};
