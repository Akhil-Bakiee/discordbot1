# Discord Spotlight Bot

A Discord bot that creates daily user spotlights with anonymous and public compliment systems to spread positivity in your server!

## Features

### 🌟 Daily Spotlight
- Automatically selects a random user every day at 12:00 UTC
- Announces the spotlight in a designated channel
- Users can opt-out of being selected

### 💌 Compliment System
- **Public compliments**: Sent in server channels with sender's name visible
- **Anonymous compliments**: Sent via DM to the bot for privacy
- Daily delivery of all compliments to the spotlighted user

### 🛠️ Management Commands
- Manual spotlight triggering for testing
- Opt-out/opt-in system for users
- Status checking and bot information

## Setup Instructions

### 1. Discord Bot Setup
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application and bot
3. Copy the bot token
4. Enable the following bot permissions:
   - Send Messages
   - Read Messages
   - Read Message History
   - Mention Everyone
   - Use Slash Commands (optional)

### 2. Bot Intents
Make sure to enable these intents in the Discord Developer Portal:
- Server Members Intent
- Message Content Intent

### 3. Environment Variables
Set the following environment variable:
```bash
export TOKEN=your_discord_bot_token_here
