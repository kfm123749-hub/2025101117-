// 실습 4. HTML 페이지 응답 - fs.createReadStream, pipe
const http = require("http");
const fs = require("fs");

const server = http.createServer((req, res) => {
  res.setHeader("Content-Type", "text/html");
  const readStream = fs.createReadStream(__dirname + "/index.html", "utf8");
  readStream.pipe(res);
});

// Render 같은 클라우드에서는 포트 번호를 PORT 환경 변수로 알려 주므로 그 값을 우선 사용
const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`${PORT}번 포트에서 서버 실행 중`); // 백틱(`)이어야 ${PORT}가 숫자로 바뀜
});
