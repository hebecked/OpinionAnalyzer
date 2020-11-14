const logger = require("tracer").console();

exports.up = function(knex) {
  return knex.schema.createTableIfNotExists("test", function (table) {
    table.timestamp("timestamp").defaultTo(knex.fn.now());
    table.integer("testXY").nullable();
    table.primary("timestamp");
  })
    .then(function () {
      logger.log("Successfully created tables!");
    });
};

exports.down = function(knex) {
  return knex.schema.dropTable("test")
};
