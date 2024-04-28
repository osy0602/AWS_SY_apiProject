const express = require("express");
const bodyParser = require("body-parser");
const mysql = require("sync-mysql");
const env = require("dotenv").config({ path: "../../.env" });
const axios = require("axios");
const app = express();

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: false }));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

var connection = new mysql({
  host: process.env.host,
  user: process.env.user,
  port: process.env.port,
  password: process.env.password,
  database: "jpjoin",
});

app.get("/Hello", (req, res) => {
  res.send("Hello World");
});

app.get("/selectJikgu", (req, res) => {
  const year = req.query.year;
  let tmp = connection.query("select * from jikgu where year=?", [year]);
  //console.log(result);
  console.log(tmp.length);
  if (tmp.length == 0) {
    const response = axios
      .get("http://0.0.0.0:3000/insertSQL?year=" + String(year))
      .then((Response) => {
        tmp = Response.data;
      });
  }
  tmp = connection.query("select * from jikgu where year=?", [year]);
  console.log(tmp);
  var result = {
    "result code": res.statusCode,
    result: tmp,
  };
  res.send(result);
});

module.exports = app;
