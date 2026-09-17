# Project endpoint
# https://scyu-1027-resource.services.ai.azure.com/api/projects/scyu-1027


from openai import OpenAI

from config import API_KEY, ENDPOINT, MODEL_NAME



client = OpenAI(
    base_url=ENDPOINT,
    api_key=API_KEY
)

response = client.responses.create(
    model=MODEL_NAME,
    input="What is the capital of France?",
)

print(f"answer: {response.output[0]}")
