# Gemini API Integration Setup

## Overview
This project now has two modes:
1. **Normal Mode** - Standard chatbot using local knowledge base
2. **Gemini Enhanced Mode** - AI-powered website navigation with Google Gemini API

## Getting Your Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your API key

## Setting Up the API Key

### Option 1: Permanent (Recommended)
Set the API key as a Windows environment variable:
```cmd
setx GEMINI_API_KEY "your-api-key-here"
```
Then restart your terminal for the change to take effect.

### Option 2: Temporary (For Testing)
Set the API key for the current session only:
```cmd
set GEMINI_API_KEY=your-api-key-here
```

## Running the Servers

### Normal Mode (Standard Chatbot)
```cmd
start_server.bat
```
- Uses local knowledge base only
- Faster responses
- No external API calls
- Good for basic queries

### Gemini Enhanced Mode (AI Navigation)
```cmd
start_server_gemini.bat
```
- Uses Google Gemini AI for intelligent responses
- Provides step-by-step website navigation
- Better understanding of complex queries
- Contextual and conversational assistance
- Requires internet connection and API key

## Features of Gemini Enhanced Mode

### Website Navigation
- **Smart Guidance**: Get step-by-step instructions for navigating the TN Government website
- **Contextual Help**: AI understands your intent and provides relevant information
- **Service Discovery**: Find departments, forms, and services easily
- **Conversational**: Natural language interaction

### Example Queries
- "How do I apply for a birth certificate?"
- "Where can I find information about property tax?"
- "Guide me through the process of getting a driving license"
- "What services are available in the revenue department?"

## Cost Considerations

- Gemini API has a free tier with generous limits
- See [Google AI Pricing](https://ai.google.dev/pricing) for details
- The free tier is sufficient for development and moderate usage

## Troubleshooting

### API Key Not Working
1. Verify your API key is correct
2. Check if the key has the necessary permissions
3. Ensure you're not exceeding rate limits

### Server Won't Start
1. Make sure virtual environment is activated
2. Install required package: `pip install google-generativeai`
3. Check that port 5000 is not already in use

### Gemini Responses Not Showing
- Check your internet connection
- Verify API key is set correctly
- Look at console output for error messages
- The system will fall back to normal mode if Gemini fails

## Comparison

| Feature | Normal Mode | Gemini Enhanced |
|---------|-------------|-----------------|
| Speed | Fast | Moderate |
| Intelligence | Basic | Advanced |
| Navigation Help | Limited | Comprehensive |
| Internet Required | No | Yes |
| API Key Required | No | Yes |
| Cost | Free | Free tier + paid |
| Use Case | Simple queries | Complex assistance |

## Recommendations

- Use **Normal Mode** for:
  - Quick information lookup
  - Development/testing
  - When offline
  
- Use **Gemini Enhanced Mode** for:
  - Website navigation assistance
  - Complex user queries
  - Better user experience
  - Production deployment with users who need guidance

## Next Steps

1. Get your API key from Google AI Studio
2. Set it as an environment variable
3. Run `start_server_gemini.bat`
4. Test with navigation-related queries
5. Compare responses with normal mode

Enjoy your AI-enhanced chatbot! 🚀
