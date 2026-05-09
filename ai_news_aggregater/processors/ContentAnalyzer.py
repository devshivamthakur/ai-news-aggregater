from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv
from ai_news_aggregater.logging.logger import logger
load_dotenv()


# =====================================================
# Response Schema
# =====================================================

class ContentResponse(BaseModel):
    title: str = Field(
        description="Professional optimized title"
    )

    summary: str = Field(
        description="Short summary 2 to 3 lines"
    )

    category: str = Field(
        description="Best matching category"
    )


# =====================================================
# Content Analyzer Class
# =====================================================

class ContentAnalyzer:

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):

        content_analyzer_model = os.getenv("CONTENT_ANALYZER_MODEL", model)
        openai_api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL")
        logger.info(f"Initializing ContentAnalyzer with model: {content_analyzer_model}")      

        # LLM
        self.llm = ChatOpenAI(
            model=content_analyzer_model,
    api_key=openai_api_key,
    base_url=base_url,
    temperature=0.3,
    extra_body={
       "chat_template_kwargs": {"enable_thinking": False},
    }
        )

        logger.info(f"ContentAnalyzer LLM initialized with model: {content_analyzer_model}")

        # Output Parser
        self.parser = PydanticOutputParser(
            pydantic_object=ContentResponse
        )

        # =====================================================
        # Prompt Template
        # =====================================================

        self.prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """
You are an advanced AI Content Analysis Assistant.

Your responsibilities:

1. Analyze both TITLE and CONTENT carefully.
2. Generate a professional and optimized title.
3. Create a concise summary in STRICTLY 2 to 3 lines.
4. Detect the most accurate category.
5. Return ONLY valid structured JSON.
6. Avoid extra explanations.
7. Summary must be clean, readable, and informative.
8. Choose category based on dominant topic.
9. Keep title attractive and professional.

Supported Categories:
- AI
- Technology
- Programming
- Finance
- Health
- Education
- Business
- Sports
- Entertainment
- Science
- Lifestyle

=====================================================
EXAMPLES
=====================================================

Example 1:

INPUT:
Title: React Native Performance Optimization
Content:
React Native applications can be optimized using memoization,
lazy loading, FlatList optimization, and avoiding unnecessary renders.

OUTPUT:
{{
    "title": "React Native Performance Optimization",
    "summary": "Improve React Native apps using memoization, lazy loading, and render optimization.",
    "category": "Programming"
}}

-----------------------------------------------------

Example 2:

INPUT:
Title: AI in Healthcare
Content:
Artificial Intelligence helps doctors detect diseases faster,
improves diagnostics, and automates healthcare operations.

OUTPUT:
{{
    "title": "AI Transforming Healthcare",
    "summary": "AI improves diagnostics, disease detection, and healthcare automation.",
    "category": "AI"
}}

-----------------------------------------------------

Example 3:

INPUT:
Title: Stock Market Basics
Content:
The stock market allows investors to buy and sell company shares
to generate profit over time.

OUTPUT:
{{
    "title": "Introduction to Stock Market",
    "summary": "Learn how investors trade company shares to build long-term profits.",
    "category": "Finance"
}}

=====================================================

{format_instructions}
                """
            ),
            (
                "human",
                """
Analyze the following content.

TITLE:
{title}

CONTENT:
{content}
                """
            )
        ])

        # =====================================================
        # Chain
        # =====================================================

        self.chain = (
            self.prompt
            | self.llm
            | self.parser
        )

    # =====================================================
    # Main Processing Method
    # =====================================================

    async def process_content(self, title: str, content: str):
        logger.info(f"Processing content with title: {title[:30]}...")

        response = await self.chain.ainvoke({
            "title": title,
            "content": content,
            "format_instructions": self.parser.get_format_instructions()
        })
        logger.info(f"Content analysis completed for title: {title[:30]}...")
        

        return response

ContentAnalyzerInstance = ContentAnalyzer(
    api_key=os.getenv("OPENAI_API_KEY")
)

# =====================================================
# Example Usage
# =====================================================

if __name__ == "__main__":

    analyzer = ContentAnalyzer(
        api_key="YOUR_OPENAI_API_KEY"
    )

    result = analyzer.process_content(
        title="LangChain Output Parser Guide",
        content="""
        LangChain output parsers help developers structure LLM responses
        into JSON, Pydantic models, and typed objects for reliable AI systems.
        """
    )

    print("\n========== FINAL OUTPUT ==========")
    print("Title:", result.title)
    print("Summary:", result.summary)
    print("Category:", result.category)