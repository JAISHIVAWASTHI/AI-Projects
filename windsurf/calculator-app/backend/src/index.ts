import express, { Request, Response } from 'express';
import cors from 'cors';
import { calculate } from './services/calculator';

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors());
app.use(express.json());

// Routes
app.get('/api/health', (req: Request, res: Response) => {
  res.status(200).json({ status: 'ok', message: 'Calculator API is running' });
});

app.post('/api/calculate', (req: Request, res: Response) => {
  try {
    const { expression } = req.body;
    
    if (!expression) {
      return res.status(400).json({ error: 'Expression is required' });
    }

    const result = calculate(expression);
    res.json({ result });
  } catch (error) {
    res.status(400).json({ error: error instanceof Error ? error.message : 'Invalid expression' });
  }
});

// Start server
app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});

export default app;
