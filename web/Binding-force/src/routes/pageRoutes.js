import { Router } from "express";
import { requireAuth } from "../middlewares/requireAuth.js";
import { requireRole } from "../middlewares/requireRole.js";
import { getJkuUrl, getPublicJwk } from "../services/jwtService.js";
import { getTokenFromRequest } from "../utils/auth.js";

const FLAG = process.env.FLAG || "SHELLMATES{fake_flag}";

const router = Router();

router.get("/", (req, res) => {
  res.render("index", { user: req.user || null });
});

router.get("/profile", requireAuth, (req, res) => {
  res.render("profile", {
    user: req.user,
    token: getTokenFromRequest(req),
    jku: getJkuUrl(),
  });
});

router.get("/power", requireAuth, requireRole("uchiha"), (req, res) => {
  res.render("power", { flag: FLAG, user: req.user || null });
});

router.get("/.well_know/jwks.json", (req, res) => {
  res.json({ keys: [getPublicJwk()] });
});

router.get("/healthz", (req, res) => {
  res.json({ ok: true });
});

export default router;
