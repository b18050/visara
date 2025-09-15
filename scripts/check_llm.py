from agents.report_agent import ReportAgent

agent = ReportAgent(
    api_key=None,
    prompt_template='x',
    use_llm=True,
    provider='ollama',
    base_url='http://localhost:11434/v1',
    model='phi3:mini',
)
print('provider=', agent.provider)
print('use_llm=', agent.use_llm)
print('client_is_none=', agent._client is None)
