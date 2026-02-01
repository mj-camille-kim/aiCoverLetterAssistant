'use strict';

/** @type {import('sequelize-cli').Migration} */
module.exports = {
  async up (queryInterface, Sequelize) {
    // userExperience 테이블에서 rawText 컬럼 삭제
    await queryInterface.removeColumn('userExperience', 'rawText');
  },

  async down (queryInterface, Sequelize) {
    // 마이그레이션 취소 시 rawText 컬럼을 다시 생성 (복구용)
    // 데이터 타입은 기존에 사용하시던 타입(예: TEXT 또는 STRING)으로 지정하세요.
    await queryInterface.addColumn('userExperience', 'rawText', {
      type: Sequelize.TEXT,
      allowNull: true, // 기존 설정에 맞춰 수정하세요
    });
  }
};