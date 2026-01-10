# Security Policy

## Handling Secrets and Sensitive Data

### Protecting Your Credentials

This project requires sensitive credentials including Telegram bot tokens and chat IDs. Follow these guidelines to keep your credentials secure:

1. **Never commit secrets to version control**
   - Always keep your `.env` file local and never commit it to Git
   - The `.gitignore` file is configured to exclude `.env` and similar files
   - Double-check before committing that no secrets are included in your changes

2. **Use environment variables**
   - Store all sensitive configuration in the `.env` file
   - Use the provided `.env.example` as a template
   - Never share your actual `.env` file with others

3. **Rotate tokens if exposed**
   - If you accidentally commit or expose your Telegram bot token, rotate it immediately:
     1. Go to [@BotFather](https://t.me/botfather) on Telegram
     2. Use the `/mybots` command
     3. Select your bot
     4. Choose "Bot Settings" → "Regenerate Token"
     5. Update your `.env` file with the new token
   - If your bot token is exposed in a Git repository, rotating the token is essential as the repository history will still contain the old token

4. **State files and local data**
   - Files like `config_state.json`, `trades.json`, and other state files may contain sensitive information
   - These files are automatically ignored by `.gitignore`
   - Do not manually commit these files to version control

## Reporting Security Vulnerabilities

If you discover a security vulnerability in this project, please report it by:

1. Opening a GitHub issue with the "security" label (if it doesn't expose sensitive details)
2. For sensitive vulnerabilities, contact the repository maintainer directly

## Best Practices

- Regularly review your `.env` file to ensure all credentials are current
- Use different bot tokens for development and production environments
- Limit access to your production `.env` file
- Regularly check for dependency updates to address security vulnerabilities
- Only share your chat ID with trusted users who should have access to the bot

## Secure Configuration

The bot includes security features:
- Single chat ID restriction to prevent unauthorized access
- Configuration stored locally in `.env` and state files
- No hardcoded credentials in the codebase

Always follow the security guidelines in this document to maintain the security of your bot deployment.
