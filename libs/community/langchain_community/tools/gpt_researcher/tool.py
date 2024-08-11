from langchain_community.utilities.gpt_researcher import ReportType, GPTRInput
import asyncio
import logging
from typing import Optional, Type, Literal
from tenacity import retry, stop_after_attempt, wait_exponential
from gpt_researcher import GPTResearcher

from langchain_core.callbacks import CallbackManagerForToolRun, AsyncCallbackManagerForToolRun
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.tools import BaseTool


# Logging to assist with debugging
logger = logging.getLogger(__name__)


# Base class for Local and Web inheritance implementing BaseTool runnables
class BaseGPTResearcher(BaseTool):
    """Base class for GPTResearcher tools performing topic research to produce reports."""
    name: str = "base_gpt_researcher"
    description: str = "Base tool for researching and producing detailed information about a topic or query."
    args_schema: Type[BaseModel] = GPTRInput
    report_type: ReportType = Field(default=ReportType.RESEARCH)
    report_source: Literal["local", "web"] = Field(default="web")

    def __init__(self, report_type: ReportType = ReportType.RESEARCH, report_source: Literal["local", "web"] = "web"):
        super().__init__(report_type=report_type, report_source=report_source)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def get_report(self, query: str) -> str:
        """
        Generate a report using GPTResearcher.

        Args:
            query (str): The research query.

        Returns:
            str: The generated report.

        Raises:
            ValueError: If there's an error generating the report.
        """
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
            logger.error(f"Error generating report: {str(e)}")
            raise ValueError(f"Error generating report: {str(e)}")

    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """
        Run the research synchronously.

        Args:
            query (str): The research query.
            run_manager (Optional[CallbackManagerForToolRun]): The callback manager.

        Returns:
            str: The generated report.
        """
        try:
            return asyncio.run(self.get_report(query=query))
        except Exception as e:
            logger.error(f"Error in _run: {str(e)}")
            raise

    async def _arun(self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        """
        Run the research asynchronously.

        Args:
            query (str): The research query.
            run_manager (Optional[AsyncCallbackManagerForToolRun]): The async callback manager.

        Returns:
            str: The generated report.
        """
        try:
            return await self.get_report(query=query)
        except Exception as e:
            logger.error(f"Error in _arun: {str(e)}")
            raise


# Running Local GPT-Researcher
class LocalGPTResearcher(BaseGPTResearcher):
    """
    Tool using GPTResearcher (local) to produce reports based on local data. 
    NOTE: Before using this tool, export `DOC_PATH` as an environment variable that must point to your directory of files that GPT-Researcher will conduct research on.
    """
    name: str = "local_gpt_researcher"
    description: str = "Utilize this tool to conduct thorough research on a specific topic or query by accessing data and files from your local directory."  
    def __init__(self, report_type: ReportType = ReportType.RESEARCH):
        super().__init__(report_type=report_type, report_source="local")


# Running Web GPT-Researcher
class WebGPTResearcher(BaseGPTResearcher):
    """Tool using GPTResearcher (web) to produce reports based on web data."""
    name: str = "web_gpt_researcher"
    description: str = "Utilize this tool to conduct thorough research on a specific topic or query using the internet."
    def __init__(self, report_type: ReportType = ReportType.RESEARCH):
        super().__init__(report_type=report_type, report_source="web")
