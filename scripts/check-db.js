/**
 * DB 내용 확인 스크립트
 * 사용: 프로젝트 루트에서 node scripts/check-db.js
 */
require('dotenv').config();
const { sequelize, User, UserExp } = require('../server/models');

async function checkDb() {
  try {
    await sequelize.authenticate();
    console.log('DB 연결 성공\n');

    console.log('=== userInfo (회원) ===');
    const users = await User.findAll({ attributes: ['id', 'userEmail', 'nickName', 'createdAt'], raw: true });
    console.table(users.length ? users : [{ message: '데이터 없음' }]);

    console.log('\n=== userExperience (경험) ===');
    const exps = await UserExp.findAll({
      attributes: ['id', 'userEmail', 'title', 'createdAt'],
      limit: 20,
      raw: true
    });
    console.table(exps.length ? exps : [{ message: '데이터 없음' }]);
    if (exps.length >= 20) console.log('(최대 20건만 표시)\n');

    process.exit(0);
  } catch (err) {
    console.error('DB 연결/조회 실패:', err.message);
    process.exit(1);
  }
}

checkDb();
