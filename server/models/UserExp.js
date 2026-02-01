module.exports = (sequelize, DataTypes) => {
    const UserExperience = sequelize.define('UserExperience', {
      id: {
        type: DataTypes.INTEGER,
        primaryKey: true,
        autoIncrement: true,
        allowNull: false
      },
      userEmail: {
        type: DataTypes.STRING(100),
        allowNull: false,
      },
      title: {
        type: DataTypes.STRING(255),
        allowNull: true
      },
      classifySTARI: {
        type: DataTypes.JSON,
        allowNull: true
      },
      keywords: {
        type: DataTypes.JSON,
        allowNull: true
      }
    }, {
      tableName: 'userExperience',
      timestamps: true,
    });
  
    return UserExperience;
  };