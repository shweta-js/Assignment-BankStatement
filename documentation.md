
Gen AI / Agentic AI Financial Data Reconciliation

This document explains the methodology and framework used to reconcile financial data from two sources: an ERP system (Excel) and a Bank Statement (PDF). The solution was developed using an Agentic AI framework, where a series of specialized AI agents cooperate to automate the end-to-end reconciliation process.

1. Overall Approach: The Agentic Framework

The reconciliation problem was broken down into a pipeline of distinct, logical steps, with each step handled by a dedicated AI "agent." This modular design allows for clear separation of concerns, making the solution robust, scalable, and easy to understand. The entire Python script (reconciliation.py) serves as the orchestrator for these agents.

    Agent 1: The File Reader Agent

        Purpose: To ingest raw data from different file formats.

        Action: Read the structured data from the .xlsx file using pandas and the semi-structured table data from the .pdf file using pdfplumber.

    Agent 2: The Data Cleaner Agent

        Purpose: To apply intelligent reasoning to standardize and prepare the data for matching.

        Key Gen AI Application: This agent demonstrates a core Generative AI capability by inferring and extracting a primary key. It uses a regular expression (r'(INV\d+)') to extract the unstructured invoice ID from the Bank Statement's Description column, creating a new, structured Invoice_ID column. This is a crucial step that enables accurate matching.

    Agent 3: The Transaction Matching Agent

        Purpose: To perform the core reconciliation and classify transactions.

        Action: Performed a robust outer merge on the Invoice_ID column to capture all transactions from both sources. It then applied a logical function to classify each transaction based on a set of professional rules, including checking for an Amount Mismatch with a small tolerance.

    Agent 4: The Report Generation Agent

        Purpose: To present the reconciliation findings in a clear, actionable format for human review.

        Key Gen AI Application: This agent demonstrates content generation. It dynamically calculates key metrics (e.g., overall reconciliation rate) and generates a professional, natural-language report that summarizes the findings and provides specific recommendations for follow-up actions. It also exports the data into a multi-sheet Excel file for detailed analysis.

3. Conclusion

This solution successfully leverages an Agentic AI framework to automate a complex financial process. It moves beyond simple scripting by incorporating AI-driven reasoning for data cleaning and generative capabilities for reporting, demonstrating a powerful and practical application of Gen AI in finance.
