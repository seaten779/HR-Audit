# HR Audit Data Directory

This directory contains sample data and scenarios for the HR Audit system.

## Files

- `sample_hr_data.json` - Sample employee data for testing and demonstration
- `audit_scenarios.json` - Predefined audit scenarios and checklists

## Important Notes

⚠️ **SECURITY NOTICE**: This directory contains only sample/demo data. Real employee data, personal information, financial records, or any sensitive information should NEVER be committed to this repository.

## Sensitive Data Guidelines

The following types of files are automatically excluded via .gitignore:
- `customer_data.json` - Contains real financial data
- `transaction_data.json` - Contains real transaction records
- `employee_data.json` - Contains real employee information
- Any files in `confidential/`, `sensitive/`, or `personal_info/` directories

## Usage

These sample files can be used for:
- Development and testing
- Demonstration purposes
- Template for data structure
- Integration testing with safe data

For production use, ensure all sensitive data is properly secured and never committed to version control.