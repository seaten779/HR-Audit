# API Keys Setup Instructions

## Environment Configuration

Your API keys have been configured in the `config.env` file. To activate them:

1. **Rename the configuration file:**
   ```bash
   cd backend
   mv config.env .env
   ```

2. **Verify the configuration:**
   - Nessie API Key: `4f119923c5fe7eb9cd7fdb886914cbb5`
   - Google Gemini API Key: `AIzaSyDkjWyS4OvusdcVH03M9-QMSVQ_pfPiqYk`

## API Services Configured

### 1. Nessie API (Capital One)
- **Purpose**: Real banking data and transaction simulation
- **Status**: Enabled (`ENABLE_NESSIE_API=true`)
- **Usage**: The transaction simulator will use real banking APIs when enabled

### 2. Google Gemini API
- **Purpose**: AI-powered content generation for notifications
- **Status**: Enabled
- **Model**: gemini-2.5-flash
- **Usage**: Generates intelligent email content and phone call scripts

## Next Steps

1. **Install dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Start the backend server:**
   ```bash
   python main.py
   ```

3. **Test the configuration:**
   - The system will automatically test the API connections on startup
   - Check the logs for "✅ Gemini service initialized successfully"
   - Check the logs for Nessie API connection status

## Security Notes

- The `.env` file contains sensitive API keys
- Never commit the `.env` file to version control
- The `config.env` file is safe to commit as it's just a template

## Troubleshooting

If you encounter issues:

1. **Gemini API not working:**
   - Verify the API key is correct
   - Check if you have sufficient quota
   - Ensure the API is enabled in Google Cloud Console

2. **Nessie API not working:**
   - Verify the API key is correct
   - Check if the API key has the necessary permissions
   - Ensure you're using the correct base URL

3. **Configuration not loading:**
   - Ensure the file is named `.env` (not `config.env`)
   - Check that the file is in the `backend/` directory
   - Verify the environment variable names match exactly
