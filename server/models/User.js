module.exports = (sequelize, DataTypes) => {
    const User = sequelize.define('User', {
      userEmail: {
        type: DataTypes.STRING(100),
        allowNull: false,
        unique: true,
        validate: { isEmail: true }
      },
      userPassword: {
        type: DataTypes.STRING(255),
        allowNull: false
      },
      nickName: {
        type: DataTypes.STRING(50),
        allowNull: false
      }
    }, {
      tableName: 'userInfo', 
      timestamps: true,
    });
  
    return User;
  };