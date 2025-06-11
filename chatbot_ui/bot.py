from openai import OpenAI
from django.conf import settings

class ChatBot:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-3.5-turbo"
        self.system_message = """You are MDDI Insights Assistant, an AI that analyzes Isentia's Daily News Reports 
        to help users uncover key topics, emerging trends, and insightful narratives. 
        Be specific and detailed in your responses, focusing on media analysis and insights."""

    def get_response(self, message, thread_id=None):
        try:
            messages = [
                {"role": "system", "content": self.system_message},
                {"role": "user", "content": message}
            ]

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )

            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}" 