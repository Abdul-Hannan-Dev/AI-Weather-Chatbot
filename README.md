# AI Weather Chatbot

A simple AI chatbot built with Python and Streamlit that integrates weather data lookup capabilities using Groq's free API and OpenWeatherMap.

## Features

- 🤖 **AI-Powered Chat**: Uses Groq's Llama 3.1 70B model for intelligent conversations
- 🌤️ **Weather Tools**: Mandatory weather lookup functionality for any city worldwide
- 💬 **System Prompt**: Pre-configured personality and behavior
- 🎨 **Clean UI**: Built with Streamlit for a smooth chat experience

## Prerequisites

1. **Groq API Key** (Free)
   - Sign up at [console.groq.com](https://console.groq.com)
   - Create an API key

2. **OpenWeatherMap API Key** (Free)
   - Sign up at [openweathermap.org/api](https://openweathermap.org/api)
   - Get your free API key (1000 calls/day on free tier)

## Installation

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables**:
   - Copy `.env.example` to `.env`:
     ```bash
     copy .env.example .env
     ```
   - Edit `.env` and add your API keys:
     ```
     GROQ_API_KEY=your_groq_api_key_here
     OPENWEATHER_API_KEY=your_openweather_api_key_here
     ```

## Usage

Run the chatbot:
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Example Queries

- "What's the weather in Tokyo?"
- "How's it looking in London today?"
- "Tell me the temperature in New York"
- Or just have a normal conversation!

## Architecture

- **Frontend**: Streamlit for interactive chat UI
- **AI Model**: Groq API with Llama 3.1 70B model
- **Weather Data**: OpenWeatherMap API
- **Tool Calling**: Function calling mechanism for weather lookups
- **System Prompt**: Mandatory injection to define chatbot behavior

## File Structure

```
ai-weather-chatbot/
├── app.py              # Main application
├── requirements.txt    # Python dependencies
├── .env.example       # Environment variables template
└── README.md          # This file
```

## Notes

- The chatbot has a mandatory system prompt that defines its personality and capabilities
- Weather tool is automatically available and called when users ask about weather
- Chat history is maintained during the session
- Temperature is displayed in Celsius
