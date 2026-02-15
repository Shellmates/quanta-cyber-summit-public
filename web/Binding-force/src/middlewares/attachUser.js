import { verifyToken } from '../services/jwtService.js';
import { getTokenFromRequest } from '../utils/auth.js';

export async function attachUser(req, res, next) {
  const token = getTokenFromRequest(req);
  if (!token) {
    return next();
  }

  try {
    const { payload } = await verifyToken(token);
    req.user = payload;
  } catch (error) {
    res.clearCookie('token');
  }

  return next();
}
