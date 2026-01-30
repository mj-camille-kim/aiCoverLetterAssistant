// @app.post("/analyze/pdf"), @app.post("/analyze/json") 등을 호출하는 파일입니다.
const express = require('express');
const router = express.Router();

// 클라이언트는 /api/aiTools/analyzePdf 호출을 하면 됩니다.
router.post('/analyzePdf', async (req, res) => {
  try {
    // 여기서 이제 여기서 /analyze/pdf 호출을 하면 됩니다.
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: '서버 내부 오류가 발생했습니다.' });
  }
});

module.exports = router;