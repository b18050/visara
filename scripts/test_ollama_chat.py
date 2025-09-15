from openai import OpenAI

client = OpenAI(base_url="http://localhost:11434/v1", api_key="")
resp = client.chat.completions.create(
    model="phi3:mini",
    messages=[{"role": "user", "content": "Reply with just: OK"}],
    temperature=0,
    max_tokens=8,
)
print(resp.choices[0].message.content)
