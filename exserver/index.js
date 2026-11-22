// Express로 서버를 만들고 실행 포트를 설정한다.
const express = require("express");
const app = express();
const PORT = Number(process.env.PORT) || 3000;

app.get("/", (req, res) => {
  res.status(200).send("Hello, Node");
});

// 오전반: 같은 URL이라도 HTTP 메서드별로 핸들러를 등록한다.
app.get("/home", (req, res) => {
  res.status(200).send("HOME");
});

app.get("/about", (req, res) => {
  res.status(200).send("ABOUT");
});

app.post("/about", (req, res) => {
  res.status(200).send("ABOUT");
});

app.get("/user/:id", (req, res) => {
  const userId = req.params.id;
  res.status(200).send(`${userId} 사용자에 대한 정보 요청`);
});

// 오후반: 사용자 목록·생성 요청과 라우트 파라미터를 실습한다.
app.get("/users", (req, res) => {
  res.status(200).send("Get all users");
});

app.post("/users", (req, res) => {
  res.status(200).send("Create new user");
});

app.get("/users/:id", (req, res) => {
  const userId = req.params.id;
  res.status(200).send(`${userId} 사용자 정보 요청`);
});

app.listen(PORT, () => {
  console.log(`${PORT} 포트로 서버 실행`);
});
