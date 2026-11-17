// 오류 처리 미들웨어: 매개변수가 4개(err, req, res, next)여야 Express가 오류 처리용으로 인식함
// err.message: 오류 메시지, err.name: 오류 이름, err.stack: 오류 발생 위치, err.statusCode: 상태 숫자
const errorHandler = (err, req, res, next) => {
  const status = err.statusCode || 500;
  switch (status) {
    case 400:
      res.status(400).send({ error: 'Bad Request' });
      break;
    case 401:
      res.status(401).send({ error: 'Unauthorized' });
      break;
    case 403:
      res.status(403).send({ error: 'Forbidden' });
      break;
    case 404:
      res.status(404).send({ error: 'Not Found' });
      break;
    case 500:
      res.status(500).send({ error: 'Internal Server Error' });
      break;
    default:
      res.status(status).send({ error: 'No Error' });
  }
};

// 모듈 내보내기
module.exports = errorHandler;
