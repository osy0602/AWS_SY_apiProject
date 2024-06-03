const mysql = require("mysql2");

const pool = mysql.createPool({
  // mysql authentication info
  host: "192.168.1.",
  user: "mysql",
  port: 3306,
  password: "",
  database: "",
});

const promisePool = pool.promise();

module.exports = promisePool;
