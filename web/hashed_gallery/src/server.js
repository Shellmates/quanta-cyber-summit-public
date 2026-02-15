import express from "express";
import path from "path";
import { fileURLToPath } from "url";
import crypto from "crypto";
import pug from "pug";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();

const PORT = Number(process.env.PORT) || 8000;

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.set("view engine", "pug");
app.set("views", path.join(__dirname, "views"));

app.disable("etag");
app.disable("x-powered-by");

app.get("/", (req, res) => {
  res.render("index", { title: "Welcome" });
});

app.post("/render", (req, res) => {
  try {
    res.status(200).send("Hello");
  } catch (error) {
    console.error("Error rendering template:", error);
    res.status(500).send(`Error`);
  }
});

process.on("uncaughtException", (err) => {
  console.error("Uncaught Exception:", err);
});

process.on("unhandledRejection", (reason, promise) => {
  console.error("Unhandled Rejection at:", promise, "reason:", reason);
});
const TOTAL_PICS = 225;
const PAGE_SIZE = 12;

// Admin password (set via environment variable `ADMIN_PASSWORD`)
const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD || "";

function requireAdmin(req, res, next) {
  if (!ADMIN_PASSWORD) return res.status(503).send("Admin not configured");

  // Check Basic auth
  const auth = req.headers.authorization || "";
  if (auth.startsWith("Basic ")) {
    try {
      const creds = Buffer.from(auth.slice(6), "base64").toString();
      const [user, pass] = creds.split(":");
      if (user === "admin" && pass === ADMIN_PASSWORD) return next();
    } catch (err) {}
  }

  // Allow query param for convenience: ?adminpw=...
  if (req.query && req.query.adminpw === ADMIN_PASSWORD) return next();

  res.set("WWW-Authenticate", 'Basic realm="Admin Area"');
  return res.status(401).send("Unauthorized");
}

function md5OfNumber(n) {
  return crypto.createHash("md5").update(String(n)).digest("hex");
}

function urlForNumber(n) {
  return `https://raw.githubusercontent.com/EkdeepSLubana/raw_dataset/refs/heads/master/ISP_processed/${n}.jpg`;
}

function sampleRandomNumbers(count) {
  const set = new Set();
  while (set.size < count) {
    const n = Math.floor(Math.random() * TOTAL_PICS) + 1;
    set.add(n);
  }
  return Array.from(set);
}

// In-memory feedback storage
const submissions = [];

app.get("/gallery", (req, res) => {
  const page = Math.max(1, parseInt(req.query.page || "1", 10));
  const pics = sampleRandomNumbers(PAGE_SIZE).map((n) => ({
    number: n,
    hash: md5OfNumber(n),
  }));
  const totalPages = Math.ceil(TOTAL_PICS / PAGE_SIZE);
  res.render("gallery", { pics, page, totalPages });
});

// API: return 10 random picture hashes
app.get("/api/picture", (req, res) => {
  const page = Math.max(1, parseInt(req.query.page || "1", 10));
  const nums = sampleRandomNumbers(PAGE_SIZE);
  const hashes = nums.map((n) => md5OfNumber(n));
  res.json({ page, hashes });
});

app.get("/api/picture/:hash", (req, res) => {
  const { hash } = req.params;
  for (let n = 1; n <= TOTAL_PICS; n++) {
    if (md5OfNumber(n) === hash) {
      return res.redirect(urlForNumber(n));
    }
  }
  res.status(404).send("Not found");
});

app.get("/feedback", (req, res) => {
  res.render("feedback");
});

app.post("/feedback", (req, res) => {
  // Accept `when` from client; fall back to server time if missing
  const { name, email, message, when } = req.body;
  // Accept `when` formatted by the client (expected `YYYY-MM-DD HH:MM`)
  const whenVal = when || new Date().toISOString();

  // Store submission
  submissions.push({ name, email, message, when: whenVal });

  // 20 example thank-you templates (Pug strings). We'll select 10 random unique ones.
  const templates = [
    `div.card\n  p Thank you, #{name} (#{email}) — received on ${when}`,
    `div.card\n  p We appreciate your input, #{name}. Time: ${when} — (#{email})`,
    `div.card\n  p #{name}, thanks for reaching out! (#{email}) at ${when}`,
    `div.card\n  p Message received from #{name} <#{email}> on ${when}`,
    `div.card\n  p Your feedback was recorded: #{name} — #{email} — ${when}`,
    `div.card\n  p #{name} (#{email}) — noted on ${when}. Thank you!`,
    `div.card\n  p Thanks for the note, #{name}! Contact: #{email}. Received: ${when}`,
    `div.card\n  p Received your submission from #{name} (#{email}) at ${when}`,
    `div.card\n  p Hello #{name}, we got your message (#{email}) on ${when}`,
    `div.card\n  p ${when} — Feedback from #{name} (#{email})`,
    `div.card\n  p Thank you for contacting us, #{name} (#{email}) — timestamp: ${when}`,
    `div.card\n  p #{name} — your message was received on ${when}. Email: #{email}`,
    `div.card\n  p Note: #{name} (#{email}) at ${when} — thanks!`,
    `div.card\n  p #{name} submitted feedback on ${when}. Contact: #{email}`,
    `div.card\n  p Appreciated, #{name}! We got it at ${when} (#{email})`,
    `div.card\n  p #{name} — submission recorded (#{email}) at ${when}`,
    `div.card\n  p Many thanks, #{name} (#{email}) — received ${when}`,
    `div.card\n  p Your feedback was captured: #{name} | #{email} | ${when}`,
    `div.card\n  p Confirmation: #{name} (#{email}) — ${when}`,
    `div.card\n  p #{name}, we've logged your message at ${when}. Email: #{email}`,
  ];
  // pick 1 random template and render it
  const idx = Math.floor(Math.random() * templates.length);
  let renderedThanks;
  try {
    // Inject `${when}` using a simple replacement so Pug still processes #{name} and #{email}
    const tplWithWhen = templates[idx];
    const fn = pug.compile(tplWithWhen);
    renderedThanks = fn({ name, email });
  } catch (e) {
    renderedThanks = `<div class="card"><p>Thanks, ${name} — ${email}</p></div>`;
  }

  // Render the feedback page directly with the rendered HTML inserted
  res.render("feedback", {
    renderedThanks,
    name,
    email,
    when: whenVal,
    message,
  });
});

app.get("/admin", requireAdmin, (req, res) => {
  res.render("admin", { submissions });
});

app.get("/robots.txt", (req, res) => {
  res.type("text/plain");
  res.send("User-agent: *\nDisallow: /admin\nAllow: /");
});

app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});
