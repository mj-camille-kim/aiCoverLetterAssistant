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

module.exports = router;