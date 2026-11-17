// express module 불러오기
const express = require('express');
// router 생성
const router = express.Router();

// 라우팅 설정
// app.js에서 기본 경로를 '/users'로 지정했으므로 여기서는 '/'와 '/:id'만 사용
router.route('/')
  // 모든 사용자 조회: GET /users
  .get((req, res) => {
    res.status(200).send('Get all users');
  })
  // 새 사용자 생성: POST /users (요청 본문을 바디파서로 파싱)
  .post((req, res) => {
    console.log(req.body);
    const { id, passwd, name, email, phone } = req.body || {};
    if (!id || !passwd || !name || !email || !phone) {
      return res.status(400).send('필수값이 입력되지 않았습니다.');
    }
    res.status(201).send('Create a new user');
  });

router.route('/:id')
  // 특정 사용자 조회: GET /users/:id
  .get((req, res) => {
    const userId = req.params.id;
    res.status(200).send(`Get user with ID: ${userId}`);
  })
  // 특정 사용자 수정: PUT /users/:id
  .put((req, res) => {
    const userId = req.params.id;
    res.status(200).send(`Update user with ID: ${userId}`);
  })
  // 특정 사용자 삭제: DELETE /users/:id
  .delete((req, res) => {
    const userId = req.params.id;
    res.status(200).send(`Delete user with ID: ${userId}`);
  });

// 모듈 내보내기
module.exports = router;
