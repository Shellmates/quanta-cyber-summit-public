import { Router } from 'express';
import authRoutes from './authRoutes.js';
import pageRoutes from './pageRoutes.js';

const router = Router();

router.use(authRoutes);
router.use(pageRoutes);

export default router;
