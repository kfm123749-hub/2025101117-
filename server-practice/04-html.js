// 실습 4. HTML 페이지 응답 - fs.createReadStream, pipe
const http = require("http");
const fs = require("fs");

const server = http.createServer((req, res) => {
  res.setHeader("Content-Type", "text/html");
  const readStream = fs.createReadStream(__dirname + "/index.html", "utf8");
  readStream.pipe(res);
});

server.listen(3000, () => {
  console.log("${PORT}번 포트에서 서버 실행 중");
});
