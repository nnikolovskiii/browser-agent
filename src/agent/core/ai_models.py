import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
kimi_llm = ChatGroq(
    model="moonshotai/kimi-k2-instruct",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key=api_key,
)

from langchain_together import ChatTogether

api_key = os.getenv("TOGETHER_API_KEY")

deepseek_llm = ChatTogether(
    model="deepseek-ai/DeepSeek-R1",
    temperature=0,
    max_tokens=1000000,
    timeout=None,
    max_retries=2,
    api_key=api_key,
)

api_key = os.getenv("GOOGLE_API_KEY")

gemini_flash_lite = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite-preview-06-17",
    api_key=api_key,
)

gemini_flash = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    api_key=api_key,
)
