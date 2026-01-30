const express = require('express');
const jwt = require('jsonwebtoken');
const router = express.Router();
const bcrypt = require('bcrypt');
const { User } = require('../models');
const key = process.env.PRIVATE_KEY || "";

router.post('/join', async (req, res) => {
  try {
    const { email, password, nickName } = req.body;

    if (!email || !password || !nickName) {
      return res.status(400).json({ message: '모든 필드를 입력해주세요.' });
    }

    const existingUser = await User.findOne({ where: { userEmail: email } });
    if (existingUser) {
      return res.status(400).json({ message: '이미 사용 중인 이메일입니다.' });
    }

    const saltRounds = 10;
    const hashedPassword = await bcrypt.hash(password, saltRounds);

    const newUser = await User.create({
      userEmail: email,
      userPassword: hashedPassword,
      nickName: nickName
    });

    res.status(201).json({ 
      message: '회원가입이 완료되었습니다!',
      user: { email: newUser.userEmail, nickName: newUser.nickName } 
    });

  } catch (error) {
    console.error(error);
    res.status(500).json({ message: '서버 내부 오류가 발생했습니다.' });
  }
});

router.post('/login', async (req, res) => {
  try {
    const { email, password } = req.body;

    if (!email || !password) {
      return res.status(400).json({ message: '모든 필드를 입력해주세요.' });
    }

    const existingUser = await User.findOne({ where: { userEmail: email } });
    if (!existingUser) {
      return res.status(400).json({ message: '존재하지 않는 이메일입니다.' });
    }

    const checkPassword = await bcrypt.compare(password, existingUser.userPassword);

    if (!checkPassword) {
      return res.status(400).json({ message: '비밀번호가 일치하지 않습니다.' });
    }

    const token = jwt.sign({email, password}, key, { expiresIn: '6h' });
    res.cookie('accessToken', token, {
        expires: new Date(Date.now() + 6 * 60 * 60 * 1000),
        httpOnly: false,
        secure: false, //배포할 때는 true로 변경
    });

    res.status(201).json({ 
      message: '로그인이 완료되었습니다!',
      success: true,
      user: {
        email: existingUser.userEmail,
        nickName: existingUser.nickName
      }
    });

  } catch (error) {
    console.error(error);
    res.status(500).json({ message: '서버 내부 오류가 발생했습니다.' });
  }
});

module.exports = router;