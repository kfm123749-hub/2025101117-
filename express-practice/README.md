# 10. Express로 서버 만들기 실습

## 폴더 구조
```
express-practice/
├─ app.js                      # 서버 생성, 미들웨어·라우터 등록, 서버 실행
├─ index.html                  # res.sendFile()로 보내는 HTML
├─ package.json                # express 의존성, start 스크립트
├─ routes/userRoutes.js        # /users 라우터 (express.Router)
└─ middlewares/errorHandler.js # 오류 처리 미들웨어
```

## 실행 방법
```bash
cd express-practice
npm install
node app.js
```
→ `Server is running on http://localhost:3000` 출력, 종료는 `Ctrl+C`

## 라우트와 실행 결과 (로컬에서 확인)

| 요청 | 결과 |
|---|---|
| GET `/` | 200 · index.html |
| GET `/json` | 200 · `{"message":"Hello Node!"}` |
| GET `/users` | 200 · `Get all users` |
| POST `/users` (필수값 모두 포함) | 201 · `Create a new user` |
| POST `/users` (필수값 누락) | 400 · `필수값이 입력되지 않았습니다.` |
| POST `/users` (잘못된 JSON) | 400 · `{"error":"Bad Request"}` (errorHandler) |
| GET `/users/apple` | 200 · `Get user with ID: apple` |
| PUT `/users/apple` | 200 · `Update user with ID: apple` |
| DELETE `/users/apple` | 200 · `Delete user with ID: apple` |

## 테스트 명령 (PowerShell)
```bash
Invoke-RestMethod -Method Post -Uri http://localhost:3000/users -ContentType "application/json" -Body '{"id":"apple","passwd":"1234","name":"kim","email":"a@a.com","phone":"010-0000-0000"}'
Invoke-RestMethod -Method Put -Uri http://localhost:3000/users/apple
Invoke-RestMethod -Method Delete -Uri http://localhost:3000/users/apple
```
Codespaces / Mac / Linux 에서는:
```bash
curl -X POST http://localhost:3000/users -H "Content-Type: application/json" -d '{"id":"apple","passwd":"1234","name":"kim","email":"a@a.com","phone":"010-0000-0000"}'
curl -X PUT http://localhost:3000/users/apple
curl -X DELETE http://localhost:3000/users/apple
```

## 슬라이드와 다르게 한 부분
- 포트: `const PORT = 3000` → `process.env.PORT || 3000` (Render 배포용)
- 슬라이드 19처럼 `router.route('/users').get('/users', ...)`로 쓰면 오류 → `.get((req, res) => ...)`로 작성
- 슬라이드 23의 `contactRoutes` → 실제 파일 이름인 `userRoutes`로 작성
- `req.body || {}`: Express 5에서는 본문 없이 POST하면 `req.body`가 `undefined`라 서버 오류가 나지 않도록 처리

## Render 설정
| 항목 | 값 |
|---|---|
| Root Directory | `express-practice` |
| Build Command | `npm install` |
| Start Command | `npm start` |
