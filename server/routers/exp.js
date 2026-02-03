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

  if (!userEmail) {
    return res.status(400).json({ success: false, message: 'userEmail이 필요합니다.' });
  }

  try {
    const experiences = await UserExp.findAll({
      where: { userEmail: userEmail.trim() },
      raw: true  // 평문 객체로 반환해 프론트에서 안정적으로 사용
    });

    res.status(200).json({
      success: true,
      data: Array.isArray(experiences) ? experiences : []
    });
  } catch (error) {
    console.error("데이터 조회 중 오류 발생:", error);
    res.status(500).json({
      success: false,
      message: '서버 내부 오류가 발생했습니다.',
      error: process.env.NODE_ENV !== 'production' ? error.message : undefined
    });
  }
});

module.exports = router;