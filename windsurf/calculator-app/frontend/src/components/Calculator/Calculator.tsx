import React, { useState, useEffect, useCallback } from 'react';
import './Calculator.css';

const Calculator: React.FC = () => {
  const [display, setDisplay] = useState('0');
  const [expression, setExpression] = useState('');
  const [lastKeyWasOperator, setLastKeyWasOperator] = useState(false);

  // Handle keyboard input
  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    const { key } = e;
    
    // Prevent default for keys we're handling
    if (/[0-9+\-*/.=]|Enter|Backspace|Escape/.test(key)) {
      e.preventDefault();
    }

    // Map keyboard keys to calculator functions
    if (/[0-9.]/.test(key)) {
      handleNumberInput(key);
    } else if (['+', '-', '*', '/'].includes(key)) {
      handleOperator(key);
    } else if (key === 'Enter' || key === '=') {
      handleEquals();
    } else if (key === 'Escape') {
      handleClear();
    } else if (key === 'Backspace') {
      handleBackspace();
    }
  }, [display, expression]);

  // Add event listener for keyboard input
  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [handleKeyDown]);

  const handleNumberInput = (num: string) => {
    if (display === '0' && num !== '.') {
      setDisplay(num);
    } else if (num === '.' && display.includes('.')) {
      // Prevent multiple decimal points
      return;
    } else {
      setDisplay(prev => prev === '0' ? num : prev + num);
    }
    setLastKeyWasOperator(false);
  };

  const handleOperator = (op: string) => {
    if (lastKeyWasOperator) {
      // Replace the last operator if the last key was an operator
      setExpression(prev => prev.slice(0, -1) + op);
    } else {
      setExpression(prev => {
        // If there's no previous expression, use the current display
        if (!prev) return `${display} ${op} `;
        return `${prev} ${display} ${op} `;
      });
      setDisplay('0');
    }
    setLastKeyWasOperator(true);
  };

  const handleEquals = async () => {
    if (!expression) return;
    
    try {
      // Combine the current expression with the display value
      const fullExpression = `${expression} ${display}`;
      
      // In a real app, you would call your backend API here
      // For now, we'll use the browser's eval (not recommended for production)
      // const response = await fetch('http://localhost:5000/api/calculate', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({ expression: fullExpression }),
      // });
      // const data = await response.json();
      // setDisplay(String(data.result));
      
      // For demo purposes only - using eval is not recommended in production
      const result = eval(fullExpression);
      setDisplay(String(result));
      setExpression('');
      setLastKeyWasOperator(false);
    } catch (error) {
      setDisplay('Error');
      setExpression('');
      setLastKeyWasOperator(false);
    }
  };

  const handleClear = () => {
    setDisplay('0');
    setExpression('');
    setLastKeyWasOperator(false);
  };

  const handleBackspace = () => {
    if (display.length === 1) {
      setDisplay('0');
    } else {
      setDisplay(prev => prev.slice(0, -1));
    }
  };

  const handlePercentage = () => {
    const value = parseFloat(display) / 100;
    setDisplay(String(value));
  };

  const handlePlusMinus = () => {
    if (display.startsWith('-')) {
      setDisplay(display.substring(1));
    } else if (display !== '0') {
      setDisplay('-' + display);
    }
  };

  return (
    <div className="calculator">
      <div className="display">
        <div className="expression">{expression}</div>
        <div className="current-display">{display}</div>
      </div>
      <div className="buttons">
        <button className="function" onClick={handleClear}>AC</button>
        <button className="function" onClick={handlePlusMinus}>±</button>
        <button className="function" onClick={handlePercentage}>%</button>
        <button className="operator" onClick={() => handleOperator('/')}>÷</button>
        
        <button onClick={() => handleNumberInput('7')}>7</button>
        <button onClick={() => handleNumberInput('8')}>8</button>
        <button onClick={() => handleNumberInput('9')}>9</button>
        <button className="operator" onClick={() => handleOperator('*')}>×</button>
        
        <button onClick={() => handleNumberInput('4')}>4</button>
        <button onClick={() => handleNumberInput('5')}>5</button>
        <button onClick={() => handleNumberInput('6')}>6</button>
        <button className="operator" onClick={() => handleOperator('-')}>-</button>
        
        <button onClick={() => handleNumberInput('1')}>1</button>
        <button onClick={() => handleNumberInput('2')}>2</button>
        <button onClick={() => handleNumberInput('3')}>3</button>
        <button className="operator" onClick={() => handleOperator('+')}>+</button>
        
        <button className="zero" onClick={() => handleNumberInput('0')}>0</button>
        <button onClick={() => handleNumberInput('.')}>.</button>
        <button className="equals" onClick={handleEquals}>=</button>
      </div>
    </div>
  );
};

export default Calculator;
