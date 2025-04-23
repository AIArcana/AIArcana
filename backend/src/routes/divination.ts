import { Router } from 'express';
import { check, validationResult } from 'express-validator';
import { DivinationController } from '../controllers/divination.controller';
import { authMiddleware } from '../middleware/auth';

const router = Router();
const divinationController = new DivinationController();

/**
 * @route   POST /api/divination/draw
 * @desc    Draw tarot cards for divination
 * @access  Public
 */
router.post(
  '/draw',
  [
    check('question', 'Question is required').not().isEmpty(),
    check('question', 'Question must be a string between 10 and 250 characters').isString().isLength({ min: 10, max: 250 }),
    check('numCards', 'Number of cards must be between 1 and 10').optional().isInt({ min: 1, max: 10 }),
    check('spread', 'Spread must be a valid spread type').optional().isString(),
  ],
  async (req, res) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    try {
      const { question, numCards = 3, spread = 'three_card' } = req.body;
      const result = await divinationController.drawCards({ question, numCards, spread });

      return res.status(200).json({
        success: true,
        data: result,
      });
    } catch (error) {
      console.error('Error drawing cards:', error);
      return res.status(500).json({
        success: false,
        message: 'Server error',
      });
    }
  }
);

/**
 * @route   POST /api/divination/interpret
 * @desc    Get AI interpretation for drawn cards
 * @access  Public
 */
router.post(
  '/interpret',
  [
    check('cards', 'Cards are required').isArray({ min: 1, max: 10 }),
    check('question', 'Question is required').not().isEmpty(),
    check('spread', 'Spread must be a valid spread type').optional().isString(),
  ],
  async (req, res) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    try {
      const { cards, question, spread = 'three_card' } = req.body;
      const result = await divinationController.getInterpretation({ cards, question, spread });

      return res.status(200).json({
        success: true,
        data: result,
      });
    } catch (error) {
      console.error('Error getting interpretation:', error);
      return res.status(500).json({
        success: false,
        message: 'Server error',
      });
    }
  }
);

/**
 * @route   POST /api/divination/premium
 * @desc    Request premium divination with advanced features
 * @access  Private (requires authentication)
 */
router.post(
  '/premium',
  authMiddleware,
  [
    check('question', 'Question is required').not().isEmpty(),
    check('spread', 'Spread is required for premium divination').not().isEmpty(),
    check('options', 'Options must be an object').optional().isObject(),
  ],
  async (req, res) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    try {
      const { question, spread, options = {} } = req.body;
      const userId = req.user.id; // From auth middleware
      
      const result = await divinationController.getPremiumDivination({
        userId,
        question,
        spread,
        options,
      });

      return res.status(200).json({
        success: true,
        data: result,
      });
    } catch (error) {
      console.error('Error with premium divination:', error);
      return res.status(500).json({
        success: false,
        message: 'Server error',
      });
    }
  }
);

/**
 * @route   GET /api/divination/history
 * @desc    Get user's divination history
 * @access  Private (requires authentication)
 */
router.get('/history', authMiddleware, async (req, res) => {
  try {
    const userId = req.user.id; // From auth middleware
    const history = await divinationController.getUserHistory(userId);

    return res.status(200).json({
      success: true,
      data: history,
    });
  } catch (error) {
    console.error('Error fetching history:', error);
    return res.status(500).json({
      success: false,
      message: 'Server error',
    });
  }
});

/**
 * @route   GET /api/divination/:id
 * @desc    Get a specific divination by ID
 * @access  Private (requires authentication)
 */
router.get('/:id', authMiddleware, async (req, res) => {
  try {
    const { id } = req.params;
    const userId = req.user.id; // From auth middleware
    
    const divination = await divinationController.getDivinationById(id, userId);
    
    if (!divination) {
      return res.status(404).json({
        success: false,
        message: 'Divination not found',
      });
    }

    return res.status(200).json({
      success: true,
      data: divination,
    });
  } catch (error) {
    console.error('Error fetching divination:', error);
    return res.status(500).json({
      success: false,
      message: 'Server error',
    });
  }
});

export default router; 