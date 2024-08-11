# GPT-Researcher Tools for LangChain

## Introduction

The `LocalGPTResearcher` and `WebGPTResearcher` tools are designed to assist with conducting thorough research on specific topics or queries. These tools leverage the power of GPT models to generate detailed reports, making them ideal for various research-related tasks. The `LocalGPTResearcher` tool accesses local data files, while the `WebGPTResearcher` retrieves information from the web.

### Key Features

- 🔬 The `LocalGPTResearcher` can work with various local file formats such as PDF, Word documents, CSVs, and more.
- 🛜 The `WebGPTResearcher` fetches data directly from the internet, making it suitable for up-to-date information gathering.
- 📝 Generate research, outlines, resources and lessons reports with local documents and web sources
- 📜 Can generate long and detailed research reports (over 2K words)
- 🌐 Aggregates over 20 web sources per research to form objective and factual conclusions
- 🖥️ Includes an easy-to-use web interface (HTML/CSS/JS)
- 🔍 Scrapes web sources with javascript support
- 📂 Keeps track and context of visited and used web sources
- 📄 Export research reports to PDF, Word and more...

---

## Installation and Setup

### Prerequisites
Ensure you have Python 3 installed on your system.

### Installation
Install the necessary packages using pip:

```bash
pip install gpt-researcher
```

### Environment Variables
For `LocalGPTResearcher`, you need to set the following environment variables:

```bash
export DOC_PATH=/path/to/your/documents
export OPENAI_API_KEY=your-openai-api-key
export TAVILY_API_KEY=your-tavily-api-key
```

For `WebGPTResearcher`, only the `OPENAI_API_KEY` and `TAVILY_API_KEY` are required:

```bash
export OPENAI_API_KEY=your-openai-api-key
export TAVILY_API_KEY=your-tavily-api-key
```

---

## Usage Examples

### LocalGPTResearcher Example
This example demonstrates how to use `LocalGPTResearcher` to generate a report based on local documents.

```python
from langchain_community.tools.gpt_researcher import LocalGPTResearcher

# Initialize the tool
researcher_local = LocalGPTResearcher(report_type="research_report")
# You can also define it as `researcher_local = LocalGPTResearcher()` - default report_type is research_report.

# Run a query
query = "What can you tell me about myself based on my documents?"
report = researcher_local.invoke({"query":query})

print("Generated Report:", report)
```

### WebGPTResearcher Example
This example shows how to use `WebGPTResearcher` to generate a report based on web data.

```python
from langchain_community.tools.gpt_researcher import WebGPTResearcher

# Initialize the tool
researcher_web = WebGPTResearcher(report_type="research_report") # report_type="research_report" is optional as the default value is `research_report`

# Run a query
query = "What are the latest advancements in AI?"
report = researcher_web.invoke({"query":query})

print("Generated Report:", report)
```

---

## Chaining with Other Components

### Example: Using `AgentExecutor` with `WebGPTResearcher`

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig, chain
from langchain.agents import AgentExecutor
from langchain_community.tools.gpt_researcher import WebGPTResearcher
from langchain.llms import ChatOpenAI

# Initialize tools and components
researcher_web = WebGPTResearcher("research_report")
tools = [researcher_web]
llm = ChatOpenAI(model="gpt-4o")
prompt = ChatPromptTemplate([
    ("system", "You are a research assistant."),
    ("human", "{input}")
])

# Create the agent
agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)
agent_executor = AgentExecutor.from_agent_and_tools(agent=agent, tools=tools, verbose=True)

# Run the agent
question = "What are the demographics of Apple Inc.?"
response = agent_executor.invoke({"input": question})

print("Agent Response:", response)
```

### Example: Chaining `LocalGPTResearcher` with Prompt and Parsing Output

```python
from langchain.prompts import ChatPromptTemplate
from langchain_community.tools.gpt_researcher import LocalGPTResearcher
from langchain.llms import ChatOpenAI

# Initialize tool
researcher_local = LocalGPTResearcher(report_type="research_report")

# Create a prompt template
prompt = ChatPromptTemplate([
    ("system", "You are a document analyzer."),
    ("human", "{input}")
])

# Run the tool with the prompt
query = "Summarize the key points from my documents."
response = researcher_local._run(prompt.format(input=query))

print("Summary:", response)
```

---

## Building from Base Class

### Extending `BaseGPTResearcher`

You can create custom tools by extending the `BaseGPTResearcher` class. Here's an example:

```python
from langchain_community.tools.gpt_researcher import BaseGPTResearcher, ReportType

class CustomGPTResearcher(BaseGPTResearcher):
    name = ""
    description = ""  
    def __init__(self, report_type: ReportType = ReportType.RESEARCH):
        super().__init__(report_type=report_type, report_source="web")

    # Override or extend methods as needed (You need to implement `_run()` method, `_arun()` is optional)
```

### Building CustomGPTResearcher

You can define a custom GPTR tool as shown below:

```python
import asyncio
from enum import Enum
from typing import Optional, Type, Literal

from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.tools import BaseTool
from gpt_researcher.master.agent import GPTResearcher

class ReportType(str, Enum):
    RESEARCH = "research_report"
    SUBTOPIC = "subtopic_report"
    CUSTOM = "custom_report"
    OUTLINE = "outline_report"
    RESOURCE = "resource_report"


class GPTRInput(BaseModel):
    """Input schema for the GPT-Researcher tool."""
    query: str = Field(description="The search query for the research")


class BaseGPTResearcher(BaseTool):
    name: str = "base_gpt_researcher"
    description: str = "Base tool for researching and producing detailed information about a topic or query."
    args_schema: Type[BaseModel] = GPTRInput
    report_type: ReportType = Field(default=ReportType.RESEARCH)
    report_source: Literal["local", "web"] = Field(default="web")

    def __init__(self, report_type: ReportType = ReportType.RESEARCH, report_source: Literal["local", "web"] = "web"):
        super().__init__(report_type=report_type, report_source=report_source)

    async def get_report(self, query: str) -> str:
        try:
            researcher = GPTResearcher(
                query=query,
                report_type=self.report_type,
                report_source=self.report_source,
                verbose=False
            )
            await researcher.conduct_research()
            report = await researcher.write_report()
            return report
        except Exception as e:
            raise ValueError(f"Error generating report: {str(e)}")

    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        return asyncio.run(self.get_report(query=query))

```

### Off-the-Shelf Usage

Alternatively, you can directly use the provided tools without modification:

```python
from langchain_community.tools.gpt_researcher import WebGPTResearcher, LocalGPTResearcher

# Use WebGPTResearcher
researcher_web = WebGPTResearcher(report_type="research_report")
report = researcher_web.invoke({'query':"What are the latest advancements in AI?"})

# Use LocalGPTResearcher
researcher_local = LocalGPTResearcher(report_type="outline_report")
report = researcher_local.invoke({'query':"Generate an outline for my upcoming project."})
```

---

## Performance Considerations

- **Time and Cost Estimates:** The tools are optimized for performance and cost, using models like `gpt-4o-mini` and `gpt-4o` (128K context) only when necessary. The average research task takes about 3 minutes and costs approximately $0.005.
- **Usage Limitations:** Be aware of potential limitations such as maximum query length and data size when working with large local datasets or complex web queries.

---

## Links and References

- **GPT-Researcher Documentation:** For a comprehensive guide, visit [GPT-Researcher Documentation](https://docs.gptr.dev/docs/gpt-researcher/introduction).
- **GitHub Repository:** Explore the code and contribute at [GPT-Researcher on GitHub](https://github.com/assafelovic/gpt-researcher).

---

## Contribution Guide

We welcome contributions to improve and extend the GPT-Researcher tools. Visit the [GitHub repository](https://github.com/assafelovic/gpt-researcher) to get started with contributing.

---

This completes the documentation for the `LocalGPTResearcher` and `WebGPTResearcher` tools. If you have any additional feedback or require further changes, feel free to let me know!