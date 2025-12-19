import streamlit as st
import os
import json
import requests
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

SYSTEM_PROMPT = """You are a helpful AI assistant with access to weather information.
You can look up current weather conditions for any city in the world.

When users ask about weather, you should use the get_weather tool to fetch real-time data.
Always be friendly, concise, and accurate in your responses.

If a user asks about weather without specifying a city, politely ask them which city they'd like to know about."""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather information for a specified city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The city name (e.g., 'London', 'New York', 'Tokyo')"
                    }
                },
                "required": ["city"]
            }
        }
    }
]


def get_weather(city: str) -> dict:
    """
    Fetch weather data from OpenWeatherMap API
    
    Args:
        city: Name of the city
        
    Returns:
        Dictionary with weather information or error message
    """
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric"  # Use Celsius
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        weather_info = {
            "city": data["name"],
            "country": data["sys"]["country"],
            "temperature": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "description": data["weather"][0]["description"],
            "wind_speed": data["wind"]["speed"]
        }
        
        return {
            "success": True,
            "data": weather_info
        }
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return {"success": False, "error": f"City '{city}' not found. Please check the spelling."}
        else:
            return {"success": False, "error": f"HTTP error occurred: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": f"Error fetching weather data: {str(e)}"}


def execute_tool_call(tool_call):
    """
    Execute the requested tool call
    
    Args:
        tool_call: Tool call object from Groq API
        
    Returns:
        JSON string with tool execution results
    """
    function_name = tool_call.function.name
    arguments = json.loads(tool_call.function.arguments)
    
    if function_name == "get_weather":
        result = get_weather(arguments["city"])
        
        if result["success"]:
            data = result["data"]
            response = f"""Weather in {data['city']}, {data['country']}:
- Temperature: {data['temperature']}°C (feels like {data['feels_like']}°C)
- Conditions: {data['description'].capitalize()}
- Humidity: {data['humidity']}%
- Wind Speed: {data['wind_speed']} m/s"""
        else:
            response = result["error"]
            
        return response
    
    return "Unknown tool"


def chat_with_groq(user_message: str) -> str:
    """
    Send message to Groq API with tool calling support
    
    Args:
        user_message: User's input message
        
    Returns:
        Assistant's response
    """
    st.session_state.messages.append({
        "role": "user",
        "content": user_message
    })
    
    api_messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ] + st.session_state.messages
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=api_messages,
            tools=TOOLS,
            tool_choice="auto",
            max_tokens=1024,
            temperature=0.7
        )
        
        response_message = response.choices[0].message
        
        if response_message.tool_calls:
            st.session_state.messages.append({
                "role": "assistant",
                "content": response_message.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    } for tc in response_message.tool_calls
                ]
            })
            
            for tool_call in response_message.tool_calls:
                tool_result = execute_tool_call(tool_call)
                
                st.session_state.messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_result
                })
            
            api_messages = [
                {"role": "system", "content": SYSTEM_PROMPT}
            ] + st.session_state.messages
            
            final_response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=api_messages,
                max_tokens=1024,
                temperature=0.7
            )
            
            final_message = final_response.choices[0].message.content
            
        else:
            final_message = response_message.content
        
        st.session_state.messages.append({
            "role": "assistant",
            "content": final_message
        })
        
        return final_message
        
    except Exception as e:
        error_message = f"Error communicating with Groq API: {str(e)}"
        st.session_state.messages.append({
            "role": "assistant",
            "content": error_message
        })
        return error_message


def main():
    """Main Streamlit application"""
    st.set_page_config(
        page_title="AI Weather Chatbot",
        layout="centered"
    )
    
    st.title(" AI Weather Chatbot")
    st.markdown("*Powered by Groq (Llama 3.1) & OpenWeatherMap*")
    
    if not os.getenv("GROQ_API_KEY") or not OPENWEATHER_API_KEY:
        st.error("API keys not found! Please set up your `.env` file with GROQ_API_KEY and OPENWEATHER_API_KEY")
        st.info("Copy `.env.example` to `.env` and add your API keys")
        st.stop()
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    for message in st.session_state.messages:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.markdown(message["content"])
        elif message["role"] == "assistant":
            with st.chat_message("assistant"):
                st.markdown(message["content"])
    
    if prompt := st.chat_input("Ask me anything or request weather information..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = chat_with_groq(prompt)
                st.markdown(response)
    
    # Sidebar with information
    with st.sidebar:
        
        st.header("Try asking:")
        st.markdown("""
        - "What's the weather in Tokyo?"
        - "How's the weather in London?"
        - "Tell me about the weather in New York"
        - Or just chat normally!
        """)
        
        if st.button("Clear Chat History"):
            st.session_state.messages = []
            st.rerun()


if __name__ == "__main__":
    main()
