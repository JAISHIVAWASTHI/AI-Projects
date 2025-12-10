data = {
    "project_title": "PG_demo_1",
    "project_key": "PGD1",
    "epic": {
        "title": "AI Loan Scoring Epic",
        "description": "Main epic for AI scoring integration",
    },
    "stories": [
        {
            "issue_type": "Story",
            "title": "Enable a digital pre-qualification journey with minimal inputs (salary, property value, tenure)",
            "description": "As a customer, I want to provide minimal inputs for pre-approval so that I can get an instant loan quote.",
            "acceptance_criteria": [
                "Customers can input salary, property value, and tenure with minimal effort",
                "The system uses AI scoring engine for real-time eligibility check",
            ],
            "effort_estimate": 5,
            "sub_tasks": [
                {
                    "title": "Design pre-qualification UI",
                    "description": "Create UI wireframes and UX flow for minimal input form",
                    "issue_type": "Sub-task",
                },
                {
                    "title": "Develop AI scoring engine integration",
                    "description": "Implement secure API connection to external data models",
                    "issue_type": "Sub-task",
                },
                {
                    "title": "Integrate with CRM system",
                    "description": "Connect pre-qualification journey with existing customer relationship data",
                    "issue_type": "Sub-task",
                },
                {
                    "title": "Test pre-approval flow",
                    "description": "Write and execute test cases for minimal input form and AI scoring engine integration",
                    "issue_type": "Sub-task",
                },
            ],
        },
        {
            "issue_type": "Story",
            "title": "Integrate AI scoring engine for real-time eligibility check",
            "description": "As a bank, I want to integrate AI scoring engine with existing customer data models so that customers can get instant loan quotes.",
            "acceptance_criteria": [
                "AI scoring engine is integrated with CRM system",
                "Real-time eligibility checks are performed using external data models",
            ],
            "effort_estimate": 4,
            "sub_tasks": [
                {
                    "title": "Evaluate existing customer data models",
                    "description": "Assess data quality and completeness for AI scoring engine integration",
                    "issue_type": "Sub-task",
                },
                {
                    "title": "Develop secure API connection to external data models",
                    "description": "Implement secure data transmission protocol",
                    "issue_type": "Sub-task",
                },
                {
                    "title": "Test AI scoring engine integration",
                    "description": "Write and execute test cases for real-time eligibility checks",
                    "issue_type": "Sub-task",
                },
            ],
        },
        {
            "issue_type": "Story",
            "title": "Introduce personalized mortgage dashboard with loan recommendations",
            "description": "As a customer, I want to see personalized loan limits using my existing relationship data and get suitable mortgage product recommendations so that I can make informed decisions.",
            "acceptance_criteria": [
                "Personalized loan limits are displayed using customer's existing relationship data",
                "Suitable mortgage products are recommended based on creditworthiness",
            ],
            "effort_estimate": 3,
            "sub_tasks": [
                {
                    "title": "Design personalized dashboard UI",
                    "description": "Create UI wireframes and UX flow for loan limit display and product recommendations",
                    "issue_type": "Sub-task",
                },
                {
                    "title": "Integrate with CRM system",
                    "description": "Connect mortgage dashboard with existing customer relationship data",
                    "issue_type": "Sub-task",
                },
                {
                    "title": "Test personalized dashboard",
                    "description": "Write and execute test cases for loan limit display and product recommendations",
                    "issue_type": "Sub-task",
                },
            ],
        },
        {
            "issue_type": "Story",
            "title": "Enable full digital loan application and document upload",
            "description": "As a customer, I want to apply for loans digitally and upload required documents securely so that I can get approval quickly.",
            "acceptance_criteria": [
                "Customers can apply for loans digitally",
                "Required documents can be uploaded securely",
            ],
            "effort_estimate": 6,
            "sub_tasks": [
                {
                    "title": "Design digital loan application UI",
                    "description": "Create UI wireframes and UX flow for digital loan application form",
                    "issue_type": "Sub-task",
                },
                {
                    "title": "Develop secure document upload mechanism",
                    "description": "Implement secure data transmission protocol for document upload",
                    "issue_type": "Sub-task",
                },
                {
                    "title": "Integrate with CRM system",
                    "description": "Connect digital loan application with existing customer relationship data",
                    "issue_type": "Sub-task",
                },
                {
                    "title": "Test digital loan application flow",
                    "description": "Write and execute test cases for digital loan application and document upload",
                    "issue_type": "Sub-task",
                },
            ],
        },
        {
            "issue_type": "Story",
            "title": "Add referral and rewards component linked to mortgage applications",
            "description": "As a bank, I want to implement referral and rewards program so that customers can earn benefits for successful loan applications.",
            "acceptance_criteria": [
                "Referral program is implemented with clear rules and incentives",
                "Rewards are issued upon successful loan application",
            ],
            "effort_estimate": 2,
            "sub_tasks": [
                {
                    "title": "Design referral program UI",
                    "description": "Create UI wireframes and UX flow for referral program display",
                    "issue_type": "Sub-task",
                },
                {
                    "title": "Develop reward issuance mechanism",
                    "description": "Implement secure data transmission protocol for reward issuance",
                    "issue_type": "Sub-task",
                },
                {
                    "title": "Test referral and rewards program",
                    "description": "Write and execute test cases for referral program and reward issuance",
                    "issue_type": "Sub-task",
                },
            ],
        },
    ],
}
