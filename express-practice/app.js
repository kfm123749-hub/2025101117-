// ① 필요한 패키지 임포트
const express = require('express');
const path = require('path');

// ② express 인스턴스(서버) 생성
const app = express();
// 포트 설정: Render 같은 클라우드에서는 PORT 환경 변수 사용, 내 컴퓨터에서는 3000
const PORT = process.env.PORT || 3000;

// ③ 라우트 외 미들웨어 등록 - 바디파서 (라우터보다 먼저 등록해야 req.body를 읽을 수 있음)
app.use(express.json()); // application/json 파싱
app.use(express.urlencoded({ extended: true })); // application/x-www-form-urlencoded 파싱

// ④ 라우트 코드, 라우터 미들웨어 등록
// res.sendFile(): HTML 문서 전송
app.get('/', (req, res) => {
  res.status(200);
  res.sendFile(path.join(__dirname, 'index.html'));
});

// res.json(): 객체를 JSON으로 변환해서 전송
app.get('/json', (req, res) => {
  res.status(200);
  res.json({ message: 'Hello Node!' });
});

// 라우팅 미들웨어 외부 파일에서 등록 (기본 경로 /users)
app.use('/users', require('./routes/userRoutes'));

// ⑤ 오류 처리 미들웨어 등록 (라우터 뒤에 등록)
app.use(require('./middlewares/errorHandler'));

// ⑥ 서버 시작
app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});
