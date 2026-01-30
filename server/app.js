
require('dotenv').config();
const express = require('express');
const path = require('path');
const cors = require('cors');
const authRouter = require('./routers/auth');
const expRouter = require('./routers/exp');
const aiToolsRouter = require('./routers/aiTools');
const { sequelize } = require('./models');
const { verifyToken } = require('./middleware/authCheck');
const cookieParser = require('cookie-parser');

const app = express();
const PORT = 3000;

app.use(cors());
app.use(cookieParser());
app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(express.static(path.join(__dirname, '../app/dist')));

sequelize.sync({ force: false }) // 반드시 false
  .then(() => console.log('DB connection success'))
  .catch(err => console.error('DB connection error:', err));

app.use('/api/auth', authRouter);
app.use('/api', expRouter);
app.use('/api/aiTools', aiToolsRouter);

app.listen(PORT, () => {
    console.log("Start Server");
});