export function requireAuth(req, res, next) {
  if (!req.user) {
    return res.status(401).render('login', {
      error: 'Please log in to continue.',
    });
  }
  return next();
}
