// express 모듈 불러오기
const express = require("express");

// express 앱 만들기
const app = express();
// 포트 설정
const PORT = Number(process.env.PORT) || 3000;

// 라우팅 설정
app.get("/", (req, res) => {
  res.status(200);
  res.send("Hello, Node");
});

// 서버 실행
app.listen(PORT, () => {
  console.log(`${PORT} 포트로 서버 실행`);
});
