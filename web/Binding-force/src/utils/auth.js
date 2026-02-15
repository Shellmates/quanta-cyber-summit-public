export function getTokenFromRequest(req) {
  const header = req.get('authorization');
  if (header && header.startsWith('Bearer ')) {
    return header.slice(7).trim();
  }
  return req.cookies.token;
}
