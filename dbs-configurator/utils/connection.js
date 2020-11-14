const knex = require('knex');
const logger = require('tracer').console();

const connection = knex({
  client: 'pg',
  connection: {
    host: 'postgres',
    user: process.env.POSTGRES_USER,
    password: process.env.POSTGRES_PASSWORD,
    database: 'postgres',
    logging: ['query', 'error']
  },
  pool: { min: 1, max: 50 },
  acquireConnectionTimeout: 200000
});

connection.migrate.latest()
  .then(function () {
    logger.log('Migration done.');
  }).catch(function (error) {
  logger.log('Error!', error);
});

module.exports = () => {
  return connection;
};
