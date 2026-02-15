import axios from 'axios';
import {
  generateKeyPair,
  exportJWK,
  importJWK,
  SignJWT,
  decodeProtectedHeader,
  jwtVerify,
} from 'jose';

const BASE_URL = process.env.BASE_URL || 'http://localhost:3000';

const keyStore = {
  kid: 'main',
  privateKey: null,
  publicJwk: null,
};
const ALLOWED_JKU_HOSTS = new Set(['localhost', 'google.com']);
const ALLOWED_JKU_SUFFIXES = ['.google.com'];

export async function initKeys() {
  const { publicKey, privateKey } = await generateKeyPair('RS256');
  const publicJwk = await exportJWK(publicKey);
  publicJwk.use = 'sig';
  publicJwk.alg = 'RS256';
  publicJwk.kid = keyStore.kid;

  keyStore.privateKey = privateKey;
  keyStore.publicJwk = publicJwk;
}

export function getJkuUrl() {
  if (!BASE_URL) {
    throw new Error('BASE_URL must be set to sign tokens.');
  }
  return `${BASE_URL}/.well_know/jwks.json`;
}

export function getPublicJwk() {
  return keyStore.publicJwk;
}

export async function signToken({ username, role, req }) {
  const jku = getJkuUrl();
  return new SignJWT({ sub: username, role })
    .setProtectedHeader({ alg: 'RS256', kid: keyStore.kid, jku })
    .setIssuedAt()
    .setExpirationTime('2h')
    .sign(keyStore.privateKey);
}

async function fetchJwk(jwksUrl, kid) {
  const response = await axios.get(jwksUrl, {
    timeout: 3000,
    validateStatus: (status) => status >= 200 && status < 300,
  });

  if (!response.data || !Array.isArray(response.data.keys)) {
    throw new Error('Invalid JWKS response');
  }

  if (kid) {
    const matching = response.data.keys.find((key) => key.kid === kid);
    if (matching) {
      return matching;
    }
  }

  if (!response.data.keys.length) {
    throw new Error('JWKS is empty');
  }

  return response.data.keys[0];
}

export async function verifyToken(token) {
  const header = decodeProtectedHeader(token);

  if (!header.jku) {
    throw new Error('Missing jku header');
  }

  let jkuUrl;
  try {
    jkuUrl = new URL(header.jku);
  } catch {
    throw new Error('Invalid jku URL');
  }

  if (!['http:', 'https:'].includes(jkuUrl.protocol)) {
    throw new Error('Unsupported jku protocol');
  }

  const hostname = jkuUrl.hostname.toLowerCase();
  const isExactHostAllowed = ALLOWED_JKU_HOSTS.has(hostname);
  const isAllowedSubdomain = ALLOWED_JKU_SUFFIXES.some((suffix) =>
    hostname.endsWith(suffix),
  );

  if (!isExactHostAllowed && !isAllowedSubdomain) {
    throw new Error('Untrusted jku host');
  }

  const jwk = await fetchJwk(header.jku, header.kid);
  const key = await importJWK(jwk, 'RS256');
  return jwtVerify(token, key, { algorithms: ['RS256'] });
}
