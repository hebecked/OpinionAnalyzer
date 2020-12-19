function init() {
    console.log('Dbs-Configurator initiated');
    const knex = require('./utils/connectDb');
}

setTimeout(init, 3000);
