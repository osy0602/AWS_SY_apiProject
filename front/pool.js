const mysql = require("mysql2");

const pool = mysql.createPool({
  // mysql authentication info
  host: "192.168.1.67",
  user: "mysql",
  port: 3306,
  password: "1234",
  database: "jpjoin",
});

const promisePool = pool.promise();

module.exports = promisePool;
