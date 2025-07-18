import os
from dotenv import load_dotenv
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential
import json

load_dotenv()
token = os.getenv("GITHUB_TOKEN")
endpoint = "https://models.github.ai/inference"
model = "openai/gpt-4.1"

if token is None:
    raise ValueError("GITHUB_TOKEN environment variable is not set.")

client = ChatCompletionsClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(token),
)

def generate_email(intent: str) -> dict:
    prompt = f"""
    You are a helpful assistant that writes professional emails.

    Based on the following request, generate a subject line and full email body:
    
    "{intent}"

    Respond in JSON with:
    {{
      "subject": "...",
      "body": "..."
    }}
    """
    try:
        response = client.complete(
            messages=[
                SystemMessage("You are a helpful assistant that writes professional emails."),
                UserMessage(prompt),
            ],
            temperature=0.7,
            top_p=1.0,
            model=model
        )
        content = response.choices[0].message.content
        return json.loads(content)
    except Exception as e:
        return {"subject": "Error generating subject", "body": f"Error: {str(e)}"} 