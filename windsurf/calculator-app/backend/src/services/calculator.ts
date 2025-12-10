interface CalculationResult {
  result: number;
  error?: string;
}

export const calculate = (expression: string): CalculationResult => {
  try {
    // Basic validation
    if (!expression || typeof expression !== 'string') {
      throw new Error('Invalid expression');
    }

    // Sanitize input to only allow numbers, basic operators, and decimal points
    const sanitizedExpression = expression
      .replace(/\s+/g, '')
      .replace(/[^-()\d/*+.]/g, '');

    // Validate the expression
    if (!isValidExpression(sanitizedExpression)) {
      throw new Error('Invalid mathematical expression');
    }

    // Use Function constructor to evaluate the expression
    // Note: In a production environment, consider using a more secure evaluation method
    const result = new Function(`return ${sanitizedExpression}`)();

    // Check if the result is a valid number
    if (typeof result !== 'number' || isNaN(result) || !isFinite(result)) {
      throw new Error('Invalid calculation result');
    }

    return { result };
  } catch (error) {
    return {
      result: 0,
      error: error instanceof Error ? error.message : 'Calculation error'
    };
  }
};

const isValidExpression = (expr: string): boolean => {
  // Check for balanced parentheses
  let balance = 0;
  for (const char of expr) {
    if (char === '(') balance++;
    if (char === ')') balance--;
    if (balance < 0) return false; // More closing parentheses than opening ones
  }
  if (balance !== 0) return false; // Unbalanced parentheses

  // Check for valid operator usage
  const operatorPattern = /[+\-*/.]/;
  for (let i = 0; i < expr.length; i++) {
    const current = expr[i];
    const next = expr[i + 1];
    
    if (operatorPattern.test(current) && operatorPattern.test(next)) {
      // Allow for negative numbers after an operator (e.g., 2*-3)
      if (!(current === '*' && next === '-') && !(current === '/' && next === '-')) {
        return false;
      }
    }
  }

  return true;
};
