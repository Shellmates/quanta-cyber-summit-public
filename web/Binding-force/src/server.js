import express from 'express';
import cookieParser from 'cookie-parser';
import morgan from 'morgan';
import path from 'path';
import { fileURLToPath } from 'url';
import routes from './routes/index.js';
import { attachUser } from './middlewares/attachUser.js';
import { initKeys } from './services/jwtService.js';

const PORT = process.env.PORT || '3000';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

await initKeys();

const app = express();

app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

app.use(morgan('tiny'));
app.use(express.urlencoded({ extended: false }));
app.use(cookieParser());
app.use(express.static(path.join(__dirname, 'public')));

app.use(attachUser);
app.use(routes);

app.listen(PORT, () => {
  console.log(`CTF app listening on :${PORT}`);
});
