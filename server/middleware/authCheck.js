const jwt = require('jsonwebtoken');

const verifyToken = (req, res, next) => {
    const token = req.cookies ? req.cookies.accessToken : null;

    if (!token) {
        req.user = null;
        return next();
    }

    try {
        const decoded = jwt.verify(token, process.env.PRIVATE_KEY);
        req.user = decoded;
        next();
    } catch (error) {
        req.user = null;
        next();
    }
};

module.exports = { verifyToken };