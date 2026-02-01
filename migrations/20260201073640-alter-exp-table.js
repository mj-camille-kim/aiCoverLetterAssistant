'use strict';

/** @type {import('sequelize-cli').Migration} */
module.exports = {
  async up (queryInterface, Sequelize) {
    // 1. 컬럼 이름 변경: classifyStart -> classifySTARI
    await queryInterface.renameColumn('userExperience', 'classifyStart', 'classifySTARI');
  },

  async down (queryInterface, Sequelize) {
    // 1. 이름 복구: classifySTARI -> classifyStart
    await queryInterface.renameColumn('userExperience', 'classifySTARI', 'classifyStart');
  }
};