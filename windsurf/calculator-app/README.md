# Calculator Application

A modern, responsive calculator web application with basic arithmetic operations, built with React and Node.js.

## Features

- Basic arithmetic operations (+, -, ×, ÷)
- Responsive design that works on all devices
- Keyboard support for better accessibility
- Error handling for division by zero and other edge cases
- Clean, modern UI

## Tech Stack

- **Frontend**: React.js with TypeScript
- **Backend**: Node.js with Express
- **Styling**: CSS Modules
- **Testing**: Jest + React Testing Library
- **Linting**: ESLint + Prettier

## Getting Started

### Prerequisites

- Node.js (v16 or higher)
- npm (v8 or higher) or yarn

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd calculator-app
   ```

2. Install dependencies for both frontend and backend:
   ```bash
   # Install frontend dependencies
   cd frontend
   npm install
   
   # Install backend dependencies
   cd ../backend
   npm install
   ```

### Running the Application

1. Start the backend server:
   ```bash
   cd backend
   npm start
   ```

2. In a new terminal, start the frontend development server:
   ```bash
   cd frontend
   npm start
   ```

3. Open [http://localhost:3000](http://localhost:3000) to view it in your browser.

## Project Structure

```
calculator-app/
├── frontend/           # Frontend React application
│   ├── public/         # Static files
│   └── src/            # Source files
│       ├── components/ # React components
│       ├── utils/      # Utility functions
│       ├── App.tsx     # Main App component
│       └── index.tsx   # Entry point
├── backend/            # Backend Node.js application
│   ├── src/            # Source files
│   │   ├── routes/     # API routes
│   │   ├── services/   # Business logic
│   │   └── index.ts    # Server entry point
│   └── package.json    # Backend dependencies
├── .gitignore         # Git ignore file
└── README.md          # This file
```

## Available Scripts

### Frontend

- `npm start` - Start the development server
- `npm test` - Run tests
- `npm run build` - Build for production
- `npm run lint` - Run ESLint

### Backend

- `npm start` - Start the server
- `npm run dev` - Start the server in development mode with nodemon
- `npm test` - Run tests

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
