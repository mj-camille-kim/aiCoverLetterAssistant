const express = require('express');
const router = express.Router();
const { UserExp } = require('../models');

router.post('/userExp', async (req, res) => {
  try {
    if (!req.body || !req.body.email) {
      return res.status(400).json({ message: '이메일이 필요합니다.' });
    }
    
    const { email } = req.body;
    const userExp = await UserExp.findAll({ where: { userEmail: email } });
    
    res.status(200).json({ 
      userExp: userExp
    });
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: '서버 내부 오류가 발생했습니다.' });
  }
});

router.post('/insertExp', async (req, res) => {
  try {
    const { email, data } = req.body;

    if (!email) {
      res.status(500);
    }

    if (data.experiences) {
      for (const exp of data.experiences) {
        await UserExp.create({
          userEmail: email || "",
          title: exp?.title || "",
          keywords: exp?.keywords || [],
          classifySTARI: exp.classifySTARI || {}
        })
      }
    }

    res.status(200).json({ 
      success: true
    });
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: '서버 내부 오류가 발생했습니다.' });
  }
});

router.post("/getUserExp", async (req, res) => {
  const { userEmail } = req.body;
  
  try {
    // 1. 결과 변수명을 'results' 또는 'experiences'로 변경하여 'res'와 구별
    const experiences = await UserExp.findAll({
      // 2. 반드시 'where' 객체 안에 조건을 넣어야 함
      where: {
        userEmail: userEmail
      }
    });

    // 3. 응답 객체 'res'를 사용하여 데이터 반환
    res.status(200).json({ 
      success: true,
      data: experiences
    });
  } catch (error) {
    console.error("데이터 조회 중 오류 발생:", error);
    // 여기서 res는 Express의 응답 객체여야 정상 작동합니다.
    res.status(500).json({ success: false, message: '서버 내부 오류가 발생했습니다.' });
  }
});

module.exports = router;