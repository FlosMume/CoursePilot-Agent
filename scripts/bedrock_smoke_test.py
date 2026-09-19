from strands import Agent
from strands.models import BedrockModel

model = BedrockModel(
    model_id="global.amazon.nova-2-lite-v1:0",
    region_name="us-west-2",
    temperature=0.2,
)

agent = Agent(model=model)

response = agent("Reply with exactly: CoursePilot Strands test successful.")
print(response)
