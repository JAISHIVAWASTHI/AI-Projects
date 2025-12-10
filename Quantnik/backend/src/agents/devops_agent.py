kk = {
    "project_title": "Calculator Application Development",
    "project_key": "CALC",
    "epic": {
        "title": "Basic Cross-Platform Calculator Implementation",
        "description": "Epic to deliver Phase-1 of the cross-platform calculator with core arithmetic operations, clean UI, and client-side execution.",
    },
    "stories": [
        {
            "issue_type": "Story",
            "title": "Addition Functionality",
            "description": "As a user, I want to perform addition operations so that I can get the sum of numbers.",
            "acceptance_criteria": [
                "Correctly calculates integer additions (e.g., 5 + 3 = 8)",
                "Correctly calculates decimal additions (e.g., 2.5 + 1.5 = 4.0)",
                "Response time <100 ms",
            ],
            "effort_estimate": 3,
            "sub_tasks": [
                {
                    "title": "Develop addition logic",
                    "description": "Implement arithmetic logic for + operator",
                    "issue_type": "Sub-task",
                },
                {
                    "title": "Write unit tests for addition",
                    "description": "Create test cases for positive/negative/decimal values",
                    "issue_type": "Sub-task",
                },
                {
                    "title": "Integrate with UI display",
                    "description": "Connect logic to display input and result",
                    "issue_type": "Sub-task",
                },
            ],
        },
        {
            "issue_type": "Story",
            "title": "Subtraction Functionality",
            "description": "As a user, I want to perform subtraction operations so that I can calculate differences between numbers.",
            "acceptance_criteria": [
                "Correctly calculates integer subtraction (e.g., 10 - 4 = 6)",
                "Correctly calculates decimal subtraction (e.g., 5.5 - 2.5 = 3.0)",
                "Response time <100 ms",
            ],
            "effort_estimate": 3,
            "sub_tasks": [
                {
                    "title": "Develop subtraction logic",
                    "description": "Implement arithmetic logic for - operator",
                    "issue_type": "Sub-task",
                },
                {
                    "title": "Write unit tests for subtraction",
                    "description": "Create test cases for positive/negative/decimal values",
                    "issue_type": "Sub-task",
                },
            ],
        },
        {
            "issue_type": "Story",
            "title": "Multiplication Functionality",
            "description": "As a user, I want to perform multiplication operations so that I can calculate products of numbers.",
            "acceptance_criteria": [
                "Correctly calculates integer multiplication (e.g., 6 * 7 = 42)",
                "Correctly calculates decimal multiplication (e.g., 2.5 * 4 = 10.0)",
                "Response time <100 ms",
            ],
            "effort_estimate": 3,
            "sub_tasks": [
                {
                    "title": "Develop multiplication logic",
                    "description": "Implement arithmetic logic for × operator",
                    "issue_type": "Sub-task",
                },
                {
                    "title": "Write unit tests for multiplication",
                    "description": "Create test cases for positive/negative/decimal values",
                    "issue_type": "Sub-task",
                },
            ],
        },
        {
            "issue_type": "Story",
            "title": "Division Functionality",
            "description": "As a user, I want to perform division operations so that I can calculate quotients of numbers.",
            "acceptance_criteria": [
                "Correctly calculates integer division (e.g., 10 / 2 = 5)",
                "Correctly calculates decimal division (e.g., 9.9 / 3 = 3.3)",
                "Displays 'Cannot divide by zero' error when divisor is 0",
                "Response time <100 ms",
            ],
            "effort_estimate": 5,
            "sub_tasks": [
                {
                    "title": "Develop division logic",
                    "description": "Implement arithmetic logic for ÷ operator",
                    "issue_type": "Sub-task",
                },
                {
                    "title": "Implement division-by-zero error handling",
                    "description": "Add error message display for invalid operations",
                    "issue_type": "Sub-task",
                },
                {
                    "title": "Write unit tests for division",
                    "description": "Create test cases for valid/invalid operations",
                    "issue_type": "Sub-task",
                },
            ],
        },
        {
            "issue_type": "Story",
            "title": "Clear/Reset Functionality",
            "description": "As a user, I want to clear inputs/reset the calculator so that I can start new calculations.",
            "acceptance_criteria": [
                "Display and input history reset when clicking clear button",
                "Keyboard shortcut (e.g., Escape key) triggers reset",
                "No residual data after reset",
            ],
            "effort_estimate": 2,
            "sub_tasks": [
                {
                    "title": "Design clear button UI",
                    "description": "Implement clear button in layout",
                    "issue_type": "Sub-task",
                },
                {
                    "title": "Develop reset logic",
                    "description": "Create function to reset display and memory",
                    "issue_type": "Sub-task",
                },
                {
                    "title": "Add keyboard shortcut support",
                    "description": "Map Escape key to reset function",
                    "issue_type": "Sub-task",
                },
            ],
        },
        {
            "issue_type": "Story",
            "title": "Decimal Support",
            "description": "As a user, I want to input and calculate decimal numbers so that I can perform precise arithmetic.",
            "acceptance_criteria": [
                "Accepts decimal inputs via UI buttons and keyboard",
                "Correctly displays decimal results (e.g., 5.5 + 2.0 shows 7.5)",
                "Handles leading/trailing zeros appropriately",
            ],
            "effort_estimate": 3,
            "sub_tasks": [
                {
                    "title": "Implement decimal button",
                    "description": "Add decimal point button to UI",
                    "issue_type": "Sub-task",
                },
                {
                    "title": "Develop decimal validation logic",
                    "description": "Validate and process decimal inputs",
                    "issue_type": "Sub-task",
                },
                {
                    "title": "Write tests for edge cases",
                    "description": "Test multi-decimal inputs and invalid formats",
                    "issue_type": "Sub-task",
                },
            ],
        },
        {
            "issue_type": "Story",
            "title": "Keyboard Input Support",
            "description": "As a user, I want to use my keyboard for inputs so that I can calculate without mouse interactions.",
            "acceptance_criteria": [
                "Numeric keys (0-9) replicate button clicks",
                "Operator keys (+, -, *, /, Enter) trigger corresponding actions",
                "Clear function maps to Escape key",
            ],
            "effort_estimate": 3,
            "sub_tasks": [
                {
                    "title": "Implement keyboard event listeners",
                    "description": "Capture key presses for numbers/operators",
                    "issue_type": "Sub-task",
                },
                {
                    "title": "Map keyboard inputs to calculator functions",
                    "description": "Connect key events to arithmetic operations",
                    "issue_type": "Sub-task",
                },
                {
                    "title": "Write cross-browser compatibility tests",
                    "description": "Verify consistent behavior in Chrome/Firefox/Edge",
                    "issue_type": "Sub-task",
                },
            ],
        },
        {
            "issue_type": "Story",
            "title": "Responsive UI Implementation",
            "description": "As a user, I want a clean responsive interface so that I can use the calculator on any device.",
            "acceptance_criteria": [
                "UI renders correctly on desktop and mobile browsers",
                "Buttons reorganize for small screens via CSS grid",
                "Display area shows real-time input and results",
            ],
            "effort_estimate": 5,
            "sub_tasks": [
                {
                    "title": "Create display area component",
                    "description": "Implement UI showing input/operation/results",
                    "issue_type": "Sub-task",
                },
                {
                    "title": "Develop responsive keypad layout",
                    "description": "Design grid-based layout with media queries",
                    "issue_type": "Sub-task",
                },
                {
                    "title": "Implement accessible button styling",
                    "description": "Ensure touch targets meet WCAG standards",
                    "issue_type": "Sub-task",
                },
            ],
        },
        {
            "issue_type": "Story",
            "title": "Browser Compatibility",
            "description": "As a user, I want the calculator to work consistently across browsers so that I can use it regardless of my browser choice.",
            "acceptance_criteria": [
                "Full functionality in Chrome (latest 2 versions)",
                "Full functionality in Firefox (latest 2 versions)",
                "Full functionality in Edge (latest 2 versions)",
            ],
            "effort_estimate": 3,
            "sub_tasks": [
                {
                    "title": "Cross-browser CSS validation",
                    "description": "Fix layout/style inconsistencies",
                    "issue_type": "Sub-task",
                },
                {
                    "title": "Cross-browser JavaScript testing",
                    "description": "Verify event handling across browsers",
                    "issue_type": "Sub-task",
                },
                {
                    "title": "Document compatibility matrix",
                    "description": "Record browser version support",
                    "issue_type": "Sub-task",
                },
                {
                    "title": "Document compatibility matrix",
                    "description": "Record browser version support",
                    "issue_type": "Sub-task",
                },
                {
                    "title": "Document compatibility matrix",
                    "description": "Record browser version support",
                },
                {
                    "title": "Document compatibility matrix",
                    "description": "Record browser version support",
                    "issue_type": "Sub-task",
                },
                {
                    "title": "Document compatibility matrix",
                    "description": "Record browser version support",
                    "issue_type": "Sub-task",
                },
            ],
        },
        {
            "title": "Document compatibility matrix",
            "description": "Record browser version support",
            "issue_type": "Sub-task",
        },
        {"title": "Document compatibility matrix"},
        {
            "title": "Document compatibility matrix",
            "description": "Record browser version support",
        },
        {"title": "Document compatibility matrix"},
        {
            "title": "Document compatibility matrix",
            "description": "Record browser version support",
        },
        {
            "title": "Document compatibility matrix",
            "description": "Record browser version support",
        },
        {"title": "Document compatibility matrix"},
        {
            "title": "Document compatibility matrix",
            "description": "Record browser version support",
            "issue_type": "Sub-task",
        },
        {
            "title": "Document compatibility matrix",
            "description": "Record browser version support",
            "issue_type": "Sub-task",
        },
        {
            "title": "Document compatibility matrix",
            "description": "Record browser version support",
            "issue_type": "Sub-task",
        },
        {
            "title": "Document compatibility matrix",
            "description": "Record browser version support",
        },
        {"title": "Document compatibility matrix"},
        {
            "title": "Document compatibility matrix",
            "description": "Record browser version support",
        },
        {"title": "Document compatibility matrix"},
        {
            "title": "Document compatibility matrix",
            "description": "Record browser version support",
            "issue_type": "Sub-task",
        },
        {
            "title": "Document compatibility matrix",
            "description": "Record browser version support",
        },
        {"title": "Document compatibility matrix"},
        {"title": "Document compatibility matrix"},
        {"title": "Document compatibility matrix"},
        {"title": "Document compatibility matrix"},
        {"title": "Document compatibility matrix"},
        {
            "title": "Document compatibility matrix",
            "description": "Record browser version support",
        },
        {"title": "Document compatibility matrix"},
        {"title": "Document compatibility matrix"},
        {"title": "Document compatibility matrix"},
        {"title": "Document compatibility matrix"},
        {
            "title": "Document compatibility matrix",
            "description": "Record browser version support",
            "issue_type": "Sub-task",
        },
    ],
}
