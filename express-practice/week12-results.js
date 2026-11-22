const express = require('express');
const path = require('node:path');
const expressPractice = require('./app');
const respondText = require('../server-practice/03-response');
const respondHtml = require('../server-practice/04-html');
const respondRoute = require('../server-practice/05-routing');

const app = express();
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'week12-results.html'));
});

app.get('/node/response', respondText);
app.get('/node/html', respondHtml);
app.use('/node/routes', respondRoute);
app.use('/express', expressPractice);

if (require.main === module) {
  const port = Number(process.env.PORT || 3000);
  app.listen(port, '0.0.0.0', () => {
    console.log(`Week 12 results are available on port ${port}`);
  });
}

module.exports = app;
