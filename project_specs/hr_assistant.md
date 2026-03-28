Problem Statement:
Organizations often struggle with inefficient HR processes, leading to decreased employee satisfaction and productivity. To address this challenge, we need to develop an AI-powered HR assistant that can automate routine HR tasks, provide personalized employee support, and enhance overall HR efficiency.

Objective:
The goal is to use AI technology to create a comprehensive HR assistant agent that can handle employee inquiries, automate HR processes, and provide personalized support to employees. The AI agent should be able to understand natural language queries and accurately and relevantly respond to employees. It should have a web application, and also provide an agent running on MCP (Model Context Protocol) server as a service for integration with other systems. Separate the web application (hr_assistant_web) and the API (hr_assistant_api) into their own projects that can be developed and deployed independently.

Incorporate these features in the project:
1. Develop a chatbot that can answer employee questions about HR policies, benefits, and procedures. The chatbot should be able to understand natural language queries and accurately and relevantly respond to employees.
2. Automate routine HR tasks such as organization rules regarding leave requests, expense claims, and employee onboarding. HR policies are provided in the [hr_policies.pdf](../hr_assistant/hr_policies.pdf) file.
3. Ensure the assistant is secure and compliant with data privacy regulations.
4. Test the assistant with real employees to gather feedback and improve its performance.
5. Provide a web application for employee registration and update (CRUD operations), and to interact with the assistant.
6. Provide an agent running on MCP (Model Context Protocol) server as a service for integration with other systems.
7. Ensure to follow industry standards for data validations on employee data entry forms.
8. Ensure to not allow prompt injection attacks.
9. Create it as a simple project for local development and testing only.

Technology Choice:
1. Use Python for the backend development.
2. Use PostgreSQL database for storing employee data.
    i) Provide the required sql script to create a suitable database schema for storing employee data (e.g., employees, benefits, etc.). Create the sql script for required database, schema, tables, indexes, and constraints in [employee_db_schema.md](../hr_assistant/employee_db_schema.md).
    ii) Use Chroma DB for vector storage and retrieval of hr policies.
    iii) Use SQLAlchemy for database operations.
3. Use React, TypeScript for the frontend development.
4. Use a web framework like Flask or Django for the web interface, to store and retrieve employee data, and to process employee queries.
5. Use OpenAI's GPT-4 or similar natural language processing library for processing employee queries.
6. Use MCP (Model Context Protocol) server as a service for integration with other systems.
7. Build a comprehensive testing suite to ensure the assistant is working as expected.
8. Document the project with clear instructions on how to set up and run the application under docs folder.
9. Build the application with a modular architecture that allows for easy maintenance and updates.
10. Ensure the application is scalable and can handle a large number of users.
11. Ensure the application is secure and compliant with data privacy regulations.
12. Ensure the application is user-friendly and accessible to all employees.
13. Ensure the application is well-documented and easy to understand.
14. Build the application with a simple and intuitive user interface.


