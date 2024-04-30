const express = require("express");
const bodyParser = require("body-parser");
const pool = require("../pool");
const axios = require("axios");
const app = express();

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: false }));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.get("/", (req, res) => {
  res.redirect("index.html");
});

app.get("/selectJikgu", async (req, res) => {
  const year = req.query.year;
  //console.log(year);
  try {
    let tmp = await pool.query("select * from jikgu where year=?", [year]);
    //console.log(tmp);
    //console.log(tmp[0].length);
    if (tmp[0].length == 0) {
      const response = await axios.get(
        "http://0.0.0.0:3000/insertSQL?year=" + String(year)
      );
    }
    tmp = await pool.query(
      "select * from jikgu where year=? order by purchase desc",
      [year]
    );
    var result = {
      "result code": res.statusCode,
      result: tmp[0],
    };
    res.send(result);
  } catch (error) {
    console.error(error);
    res.status(500).send("Internal Server Error");
  }
});

module.exports = app;
