# 2025101117-

## 12주차 웹프로그래밍 실습 · 2026.11.17

| 영상 | 실습 | 소스 코드 |
| --- | --- | --- |
| 1차시 · 약 24:36–40:42 | `http.createServer()`, `listen()`, 요청 객체, 텍스트 응답과 `res.end()` | [요청 수신](server-practice/01-server.js), [요청 객체](server-practice/02-request.js), [텍스트 응답](server-practice/03-response.js) |
| 2차시 · 약 08:54, 19:46, 41:52 | HTML 파일 스트리밍, Render 설정, `GET /home`·`GET /about`·404 | [HTML 응답 서버](server-practice/04-html.js), [HTML 파일](server-practice/index.html), [라우팅 서버](server-practice/05-routing.js) |
| 3차시 오전반 · 약 13:45, 22:59, 32:17 | Express 실행, `GET /home`, `GET`·`POST /about`, `GET /user/:id` | [Express 기본 서버](exserver/index.js), [패키지 설정](exserver/package.json) |
| 3차시 오후반 대체 녹화 · 약 12:05, 25:15, 41:43 | Express 실행, `GET`·`POST /users`, `GET /users/:id`, `res.sendFile()` | [Express 기본 서버](exserver/index.js), [HTML·JSON 응답 실습](express-practice/app.js), [HTML 파일](express-practice/index.html) |

1·2차시의 요청별 출력은 [Node.js 실습 결과](server-practice/실습결과.md)에서 확인할 수 있습니다. Express 강의자료의 사용자 수정·삭제, 본문 파싱과 오류 처리 예제는 [사용자 라우터](express-practice/routes/userRoutes.js), [오류 처리 미들웨어](express-practice/middlewares/errorHandler.js), [Express 실습 결과](express-practice/README.md)에 있습니다.

### Node.js 기본 HTTP 실습 실행

```sh
cd server-practice
node 03-response.js
```

`http://localhost:3000/`에서 `Hello Node`를 확인합니다. `01-server.js`와 `02-request.js`는 요청 수신을 관찰하는 단계라 터미널에 요청을 출력하고 브라우저는 응답을 기다립니다. `04-html.js`로 실행하면 같은 주소에서 HTML을 확인할 수 있습니다. `05-routing.js`로 실행하면 `/home`과 `/about`에 각각 `HOME`, `ABOUT`을 보내고, 미등록 경로에는 404를 보냅니다. 예제를 바꿀 때는 `Ctrl+C`로 이전 서버를 종료합니다.

2차시 Render 설정을 이 저장소에 적용할 때는 Root Directory를 `server-practice`, Build Command를 `npm install`, Start Command를 `npm start`로 지정합니다. `npm start`는 `05-routing.js`를 실행하며, HTML 파일 응답을 실행하는 단계의 Start Command는 `node 04-html.js`입니다.

### Express 실습 실행

```sh
cd exserver
npm ci
npm start
```

별도 터미널에서 아래 경로를 요청합니다. Windows PowerShell에서는 `curl` 대신 `curl.exe`를 사용할 수 있습니다.

| 요청 | 응답 |
| --- | --- |
| `GET /` | `200` · `Hello, Node` |
| `GET /home` | `200` · `HOME` |
| `GET /about` 또는 `POST /about` | `200` · `ABOUT` |
| `GET /user/apple` | `200` · `apple 사용자에 대한 정보 요청` |
| `GET /users` | `200` · `Get all users` |
| `POST /users` | `200` · `Create new user` |
| `GET /users/apple` | `200` · `apple 사용자 정보 요청` |

```sh
curl -i http://localhost:3000/home
curl -i -X POST http://localhost:3000/about
curl -i http://localhost:3000/user/apple
curl -i -X POST http://localhost:3000/users
curl -i http://localhost:3000/users/apple
```

기본 `POST /users`의 응답은 오후반 영상에서 실행한 `200`을 따릅니다. 강의자료의 `201` 응답과 필수값 확인은 [확장 사용자 라우터](express-practice/routes/userRoutes.js)에서 실행할 수 있습니다. HTML과 JSON을 확인하려면 기본 서버를 종료하고 저장소의 `express-practice` 디렉터리에서 `npm ci`와 `npm start`를 실행한 뒤 `/`와 `/json`을 엽니다.

참고 자료는 LMS의 12주차 녹화 01·02·03과 오후반 대체 녹화, 강의자료 「09. 서버 만들기」와 「10. Express로 서버 만들기」입니다. [수업용 Node.js 예제 저장소](https://github.com/blumin7/web_a/tree/main/server)
