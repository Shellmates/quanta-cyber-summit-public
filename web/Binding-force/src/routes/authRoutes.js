import { Router } from 'express';
import { users } from '../data/users.js';
import { signToken } from '../services/jwtService.js';

const router = Router();

router.get('/login', (req, res) => {
  res.render('login', { error: null });
});

router.post('/login', async (req, res) => {
  const { username, password } = req.body;
  const record = users.get(username);

  if (!record || record.password !== password) {
    return res.status(401).render('login', {
      error: 'Invalid credentials.',
    });
  }

  const token = await signToken({ username, role: record.role, req });
  res.cookie('token', token, {
    httpOnly: true,
    sameSite: 'lax',
  });

  return res.redirect('/profile');
});

router.post('/logout', (req, res) => {
  res.clearCookie('token');
  return res.redirect('/');
});

export default router;
