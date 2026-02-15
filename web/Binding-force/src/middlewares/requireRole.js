export function requireRole(role) {
  return (req, res, next) => {
    if (!req.user || req.user.role !== role) {
      return res.status(403).render('forbidden', { role, user: req.user || null });
    }
    return next();
  };
}
