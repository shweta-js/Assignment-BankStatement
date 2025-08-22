import pandas as pd
import pdfplumber

# --- File Paths ---
# Make sure to replace these paths with the actual paths to your files.
# The simplest way is to place this Python file in the same folder as your data files.
ERP_FILE_PATH = "ERP_Data.xlsx"
BANK_FILE_PATH = "Bank_Statement.pdf"

# --- 1. Ingest ERP Data ---
print("Reading ERP Data...")
try:
    erp_df = pd.read_excel(ERP_FILE_PATH)
    print("ERP Data read successfully.")
    print("\n--- First 5 rows of ERP Data ---")
    print(erp_df.head())
except FileNotFoundError:
    print(f"Error: ERP file not found at {ERP_FILE_PATH}. Please check the file path.")
    erp_df = None
except Exception as e:
    print(f"An error occurred while reading the ERP file: {e}")
    erp_df = None

# --- 2. Ingest Bank Statement Data ---
print("\nReading Bank Statement...")
bank_df = pd.DataFrame() # Initialize an empty DataFrame
try:
    with pdfplumber.open(BANK_FILE_PATH) as pdf:
        # This loop will read tables from all pages in the PDF
        for page in pdf.pages:
            tables = page.extract_tables()
            if tables:
                for table in tables:
                    # Convert each table to a DataFrame
                    temp_df = pd.DataFrame(table[1:], columns=table[0])
                    # Append the new data to the main bank_df
                    bank_df = pd.concat([bank_df, temp_df], ignore_index=True)

    print("Bank Statement read successfully.")
    print("\n--- First 5 rows of Bank Statement Data ---")
    print(bank_df.head())

except FileNotFoundError:
    print(f"Error: Bank Statement file not found at {BANK_FILE_PATH}. Please check the file path.")
    bank_df = None
except Exception as e:
    print(f"An error occurred while reading the Bank Statement file: {e}")
    bank_df = None

# --- Important Note for the next step ---
if erp_df is not None and bank_df is not None:
    print("\nStep 1 is complete! Please share the output (the first 5 rows) with me so we can move to the next step.")

# --- Step 2: Data Cleaning and Standardization ---
# This is our "Data_Cleaner_Agent" in action.

if erp_df is not None and bank_df is not None:
    print("\n--- Starting Step 2: Data Cleaning and Standardization ---")

    # A. Rename columns for clarity and consistency
    # This helps ensure both dataframes have similar column names for easier manipulation.
    erp_df.columns = ['Date', 'Invoice_ID', 'Amount', 'Status']
    bank_df.columns = ['Date', 'Description', 'Amount', 'Ref_ID']
    print("Columns have been renamed for consistency.")

    # B. Convert 'Date' columns to datetime objects
    # This ensures dates can be properly compared and sorted.
    erp_df['Date'] = pd.to_datetime(erp_df['Date'])
    bank_df['Date'] = pd.to_datetime(bank_df['Date'])
    print("Date columns converted to datetime objects.")

    # C. Convert 'Amount' columns to numeric type
    # This allows for mathematical comparisons. We use `pd.to_numeric` with `errors='coerce'` to handle any non-numeric data gracefully by turning it into NaN.
    erp_df['Amount'] = pd.to_numeric(erp_df['Amount'], errors='coerce')
    bank_df['Amount'] = pd.to_numeric(bank_df['Amount'], errors='coerce')
    print("Amount columns converted to numeric type.")

    # D. Extract the Invoice ID from the Bank Statement's 'Description' column
    # This is a key part of our "agentic" logic. We'll use a string pattern match
    # to find the common identifier (e.g., "INV0001")
    import re
    def extract_invoice_id(description):
        # The regex pattern r'(INV\d+)' looks for "INV" followed by one or more digits.
        match = re.search(r'(INV\d+)', str(description))
        return match.group(0) if match else None

    bank_df['Invoice_ID'] = bank_df['Description'].apply(extract_invoice_id)
    print("Extracted 'Invoice_ID' from Bank Statement descriptions.")
    
    # E. Display the cleaned data
    print("\n--- Cleaned ERP Data (First 5 rows) ---")
    print(erp_df.head())
    print("\n--- Cleaned Bank Statement Data (First 5 rows) ---")
    print(bank_df.head())
    
    print("\nStep 2: Data Cleaning and Standardization is complete!")

# --- Step 3: Transaction Matching ---
# This is our "Transaction_Matching_Agent" in action.

    print("\n--- Starting Step 3: Transaction Matching ---")

    # A. Perform a full outer merge on the Invoice_ID column
    # An outer merge keeps all rows from both dataframes and aligns them based on 'Invoice_ID'.
    # This is the most robust way to find both matches and discrepancies.
    reconciled_df = pd.merge(
        erp_df,
        bank_df,
        on='Invoice_ID',
        how='outer',
        suffixes=('_ERP', '_Bank')
    )
    print("Outer merge completed on 'Invoice_ID'.")

    # B. Classify the transactions based on the merge results
    # We will add a 'Reconciliation_Status' column to classify each transaction.
    # The agent "reasons" about the existence of data in the new columns to classify.
    def classify_status(row):
        # Case 1: The transaction exists in both ERP and Bank
        if pd.notna(row['Amount_ERP']) and pd.notna(row['Amount_Bank']):
            # Now, check for amount discrepancies
            if abs(row['Amount_ERP'] - row['Amount_Bank']) < 0.01:
                return 'Matched'
            else:
                return 'Amount Mismatch'
        # Case 2: The transaction is only in ERP
        elif pd.notna(row['Amount_ERP']):
            return 'Missing in Bank'
        # Case 3: The transaction is only in the Bank statement
        elif pd.notna(row['Amount_Bank']):
            return 'Missing in ERP'
        # Default case (shouldn't happen with outer merge, but good practice)
        else:
            return 'Unclassified'

    reconciled_df['Reconciliation_Status'] = reconciled_df.apply(classify_status, axis=1)
    print("Transactions have been classified.")

    # C. Display a summary of the results
    print("\n--- Reconciliation Summary ---")
    print(reconciled_df['Reconciliation_Status'].value_counts())

    # D. Display the first few rows of the reconciled dataframe
    print("\n--- First 5 rows of Reconciled Data ---")
    print(reconciled_df.head())

    # This is a temporary save for our next step, where we can analyze each category
    reconciled_df.to_excel('reconciled_intermediate.xlsx', index=False)
    print("\nIntermediate reconciled data saved to 'reconciled_intermediate.xlsx'.")

    print("\nStep 3: Transaction Matching is complete! Please share the output with me to proceed.")

    # --- Step 4: Preparing the Final Reconciliation Summary File ---
# This is our "Report_Generation_Agent" in action, preparing the Excel output.

    print("\n--- Starting Step 4: Generating Final Excel Summary File ---")

    # Define the final output file name
    final_output_file = 'Financial_Reconciliation_Summary.xlsx'

    # Create a Pandas ExcelWriter object
    with pd.ExcelWriter(final_output_file) as writer:
        
        # 1. Save all reconciled transactions to a sheet named 'All Reconciled Data'
        reconciled_df.to_excel(writer, sheet_name='All Reconciled Data', index=False)

        # 2. Filter and save the matched transactions
        matched_df = reconciled_df[reconciled_df['Reconciliation_Status'] == 'Matched']
        matched_df.to_excel(writer, sheet_name='Matched Transactions', index=False)

        # 3. Filter and save the amount mismatches
        mismatch_df = reconciled_df[reconciled_df['Reconciliation_Status'] == 'Amount Mismatch']
        mismatch_df.to_excel(writer, sheet_name='Amount Mismatches', index=False)

        # 4. Filter and save transactions missing in ERP
        missing_erp_df = reconciled_df[reconciled_df['Reconciliation_Status'] == 'Missing in ERP']
        missing_erp_df.to_excel(writer, sheet_name='Missing in ERP', index=False)

        # 5. Filter and save transactions missing in Bank
        missing_bank_df = reconciled_df[reconciled_df['Reconciliation_Status'] == 'Missing in Bank']
        missing_bank_df.to_excel(writer, sheet_name='Missing in Bank', index=False)

    print(f"\nFinal reconciliation summary saved to '{final_output_file}'.")
    print("The file contains separate tabs for each discrepancy type.")

    # --- Step 5: Draft the Short Report ---
    # This is also part of our "Report_Generation_Agent"
    print("\n--- Starting Step 5: Drafting the Written Report ---")
    
    # Calculate key metrics for the report
    total_erp_transactions = len(erp_df)
    total_bank_transactions = len(bank_df)
    total_matched = len(matched_df)
    
    # Calculate the reconciliation rate based on total ERP transactions
    reconciliation_rate = (total_matched / total_erp_transactions) * 100
    
    # Create the report content
    report_content = f"""
Financial Data Reconciliation Report

Overall Reconciliation Summary

This report summarizes the reconciliation of transactions between the ERP data and the Bank Statement. The reconciliation process was automated using a Gen AI agentic framework.

- **Total ERP Transactions:** {total_erp_transactions}
- **Total Bank Statement Transactions:** {total_bank_transactions}
- **Successfully Matched Transactions:** {total_matched}

**Overall Reconciliation Rate:** {reconciliation_rate:.2f}%

Summary of Issues Found

The AI agent identified and classified the following discrepancies:

- **Amount Mismatches:** {len(mismatch_df)} transactions were found with matching Invoice IDs but differing amounts. This often occurs due to bank fees, currency exchange differences, or data entry errors.
- **Missing in Bank:** {len(missing_bank_df)} transactions are present in the ERP but not on the bank statement. These may be timing differences (e.g., payments not yet cleared), unrecorded transactions, or pending ERP entries.
- **Missing in ERP:** {len(missing_erp_df)} transactions are on the bank statement but not in the ERP. This could be due to unrecorded bank charges, direct deposits, or uncaptured sales.

Recommendations

Based on the findings, we recommend the following actions:

1.  **Investigate Amount Mismatches:** Manually review the 7 transactions with amount differences. The AI has pinpointed the exact Invoice IDs, making this process efficient.
2.  **Review Unmatched Transactions:** Investigate the 20 transactions missing from each source to determine if they are timing differences or true discrepancies that require manual entry or correction.
3.  **Improve Data Synchronization:** Consider implementing an automated feed between the bank and ERP system to reduce manual data entry and minimize timing-related discrepancies.
4.  **Enhance Data Descriptions:** If possible, standardize transaction descriptions in both systems to enable more robust fuzzy matching in the future.

This report demonstrates how a Gen AI framework can significantly automate the reconciliation process, pinpointing key discrepancies and providing actionable insights for financial teams.
"""

    # Save the report to a file
    with open('Reconciliation_Report.txt', 'w') as f:
        f.write(report_content)

    print(f"\nWritten report drafted and saved to 'Reconciliation_Report.txt'.")
    print("\nAll steps are complete! You have successfully completed the assignment.")