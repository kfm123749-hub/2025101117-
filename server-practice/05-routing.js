// 실습 5. 라우팅 - 요청 메서드와 URL에 따라 다른 응답
const http = require("http");

function respondRoute(req, res) {
  const { method, url } = req;
  res.setHeader("Content-Type", "text/plain");
  if (method === "GET" && url === "/home") {
    res.statusCode = 200;
    res.end("HOME");
  } else if (method === "GET" && url === "/about") {
    res.statusCode = 200;
    res.end("ABOUT");
  } else {
    res.statusCode = 404;
    res.end("NOT FOUND");
  }
}

// 슬라이드 코드에는 빠져 있어 추가: 이 부분이 없으면 서버가 실행되지 않음
// Render 같은 클라우드에서는 포트 번호를 PORT 환경 변수로 알려 주므로 그 값을 우선 사용
const PORT = process.env.PORT || 3000;
if (require.main === module) {
  http.createServer(respondRoute).listen(PORT, () => {
    console.log(`${PORT}번 포트에서 서버 실행 중`);
  });
}

module.exports = respondRoute;
