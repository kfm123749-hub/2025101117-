// 실습 4. HTML 페이지 응답 - fs.createReadStream, pipe
const http = require("http");
const fs = require("fs");

function respondHtml(req, res) {
  res.setHeader("Content-Type", "text/html");
  const readStream = fs.createReadStream(__dirname + "/index.html", "utf8");
  readStream.pipe(res);
}

// Render 같은 클라우드에서는 포트 번호를 PORT 환경 변수로 알려 주므로 그 값을 우선 사용
const PORT = process.env.PORT || 3000;
if (require.main === module) {
  http.createServer(respondHtml).listen(PORT, () => {
    console.log(`${PORT}번 포트에서 서버 실행 중`);
  });
}

module.exports = respondHtml;
