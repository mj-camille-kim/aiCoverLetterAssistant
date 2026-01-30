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
      rawText: {
        type: DataTypes.TEXT,
        allowNull: true
      },
      title: {
        type: DataTypes.STRING(255),
        allowNull: true
      },
      classifyStart: {
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