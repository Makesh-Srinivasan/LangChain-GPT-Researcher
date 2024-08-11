from libs.community.langchain_community.tools.gpt_researcher.tool import WebGPTResearcher, LocalGPTResearcher

# Use LocalGPTResearcher
researcher_local = LocalGPTResearcher(report_type="research_report")
report = researcher_local.invoke({'query':"What can you tell about the company?"})

# Use WebGPTResearcher
researcher_web = WebGPTResearcher(report_type="research_report")
report = researcher_web.invoke({'query':"What are the latest advancements in AI?"})