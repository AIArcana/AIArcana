import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import morgan from 'morgan';
import dotenv from 'dotenv';
import { createConnection } from './config/database';
import apiRoutes from './routes';
import errorHandler from './middleware/errorHandler';
import logger from './utils/logger';

// Load environment variables
dotenv.config();

// Create Express server
const app = express();
const port = process.env.PORT || 3001;

// Middleware
app.use(helmet()); // Security headers
app.use(cors()); // Enable CORS
app.use(express.json()); // Parse JSON bodies
app.use(morgan('combined')); // HTTP request logger

// Connect to database
createConnection()
  .then(() => logger.info('Database connection established'))
  .catch((error) => {
    logger.error('Database connection error', error);
    process.exit(1);
  });

// Routes
app.use('/api', apiRoutes);

// Default route
app.get('/', (req, res) => {
  res.json({
    status: 'success',
    message: 'AIArcana API Server',
    version: process.env.npm_package_version || '0.1.0',
  });
});

// Error handler
app.use(errorHandler);

// Start server
app.listen(port, () => {
  logger.info(`Server running on port ${port}`);
});

// Handle graceful shutdown
process.on('SIGTERM', () => {
  logger.info('SIGTERM received, shutting down gracefully');
  // Close database connections, etc.
  process.exit(0);
});

export default app; 