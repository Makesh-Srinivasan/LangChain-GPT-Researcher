from enum import Enum
from langchain_core.pydantic_v1 import BaseModel, Field


class ReportType(str, Enum):
    RESEARCH = "research_report"
    SUBTOPIC = "subtopic_report"
    CUSTOM = "custom_report"
    OUTLINE = "outline_report"
    RESOURCE = "resource_report"


class GPTRInput(BaseModel):
    """Input schema for the GPT-Researcher tool."""
    query: str = Field(description="The search query for the research")
