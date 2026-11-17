// 실습 2. 요청 객체 살펴보기
const http = require("http");

const server = http.createServer((req, res) => {
  console.log(req);
});

server.listen(3000, () => {
  console.log("3000번 포트에서 서버 실행 중");
});
