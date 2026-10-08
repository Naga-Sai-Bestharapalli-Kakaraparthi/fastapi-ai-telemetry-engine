from pydantic import BaseModel, Field


class PromptPayload(BaseModel):
    prompt: str = Field(
        ...,
        min_length=3,
        max_length=1000,
        description="Raw prompt text or structured query input",
        example="Analyze real-time server telemetry data",
    )
    model_version: str = Field(
        default="gemini-1.5-flash",
        description="Target model version for workflow execution",
    )


class TaskResponse(BaseModel):
    status: str
    source: str
    prompt: str
    result: str
    latency_ms: float
