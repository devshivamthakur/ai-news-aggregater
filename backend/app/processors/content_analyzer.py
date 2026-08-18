import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from app.logging.logger import logger

load_dotenv()


# =====================================================
# Prompt Loading
# =====================================================

# The system prompt lives in app/prompts/content_analyzer.md so it can be
# edited without touching code. Falls back to the inline version below if the
# file is missing or unreadable.
_PROMPT_FILE = Path(__file__).resolve().parent.parent / "prompts" / "content_analyzer.md"

_INLINE_SYSTEM_PROMPT = """
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
{categories}

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


def _load_system_prompt() -> str:
    """Load the system prompt from app/prompts/content_analyzer.md."""
    try:
        content = _PROMPT_FILE.read_text(encoding="utf-8").strip()
        if content:
            logger.info("Loaded content analyzer prompt from %s", _PROMPT_FILE)
            return content
    except OSError:
        pass
    logger.warning(
        "Could not load prompt from %s - falling back to inline prompt",
        _PROMPT_FILE,
    )
    return _INLINE_SYSTEM_PROMPT


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

    def __init__(self, api_key: str | None = None, model: str = "gpt-4o-mini"):

        content_analyzer_model = os.getenv("CONTENT_ANALYZER_MODEL", model)
        openai_api_key = os.getenv("OPENAI_API_KEY", api_key)
        base_url = os.getenv("OPENAI_BASE_URL")
        logger.info(f"Initializing ContentAnalyzer with model: {content_analyzer_model}")

        self._api_key = openai_api_key
        self._model = content_analyzer_model
        self._base_url = base_url

        # The LLM is created lazily so importing this module works even when
        # OPENAI_API_KEY is unset (e.g. running the API without analysis).
        self._llm = None

        # Output Parser
        self.parser = PydanticOutputParser(
            pydantic_object=ContentResponse
        )

        # =====================================================
        # Prompt Template
        # =====================================================

        # System prompt is loaded from app/prompts/content_analyzer.md
        # (falls back to the inline constant if the file is missing).
        self.prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                _load_system_prompt(),
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
    # Lazy LLM initialization
    # =====================================================

    def _ensure_llm(self) -> ChatOpenAI:
        """Build the LLM client on first use.

        Requires OPENAI_API_KEY (or the key passed to __init__); raises a clear
        error otherwise so callers know analysis is not configured.
        """
        if self._llm is None:
            if not self._api_key:
                raise RuntimeError(
                    "ContentAnalyzer requires an OpenAI API key. Set OPENAI_API_KEY "
                    "or pass api_key to the constructor before analyzing content."
                )
            self._llm = ChatOpenAI(
                model=self._model,
                api_key=self._api_key,
                base_url=self._base_url,
                temperature=0.3,
                extra_body={
                    "chat_template_kwargs": {"enable_thinking": False},
                },
            )
            logger.info(f"ContentAnalyzer LLM initialized with model: {self._model}")
        return self._llm

    # =====================================================
    # Category list helper
    # =====================================================

    def _build_category_string(self, categories: list[str] | None = None) -> str:
        """Resolve the list of supported categories (passed in, from DB, or defaults)."""
        category_str = ""
        if categories:
            category_str = "\n".join(f"- {c}" for c in categories)
        else:
            try:
                from app.models.category import Category
                from app.storage.db import SessionLocal
                db = SessionLocal()
                try:
                    db_categories = db.query(Category).filter(Category.is_active).all()
                    if db_categories:
                        category_str = "\n".join(f"- {c.name}" for c in db_categories)
                finally:
                    db.close()
            except Exception:
                logger.warning(
                    "Could not fetch categories from DB inside "
                    "ContentAnalyzer, using defaults"
                )

        if not category_str:
            # Fallback defaults
            category_str = (
                "- AI\n- Technology\n- Programming\n- Science\n"
                "- Finance\n- Health\n- Education\n- Business\n"
                "- Sports\n- Entertainment\n- Lifestyle"
            )
        return category_str

    # =====================================================
    # Main Processing Method
    # =====================================================

    async def process_content(self, title: str, content: str, categories: list[str] | None = None):
        logger.info(f"Processing content with title: {title[:30]}...")

        category_str = self._build_category_string(categories)

        chain = self.prompt | self._ensure_llm() | self.parser
        response = await chain.ainvoke({
            "title": title,
            "content": content,
            "categories": category_str,
            "format_instructions": self.parser.get_format_instructions()
        })
        logger.info(f"Content analysis completed for title: {title[:30]}...")


        # Instead of returning a list of Pydantic objects, return a list of tuples
        # to match what the pipeline code expects.
        return [(r.title, r.summary, r.category) for r in response]

    # =====================================================
    # Batch Processing Method
    # =====================================================

    async def process_batch(
        self,
        items: list[tuple[str, str]],
        categories: list[str] | None = None,
        max_concurrency: int = 5,
    ) -> list[ContentResponse | BaseException]:
        """Analyze many (title, content) pairs in parallel.

        Uses the LangChain Runnable's native ``abatch`` support, which fans
        the individual LLM calls out concurrently instead of processing items
        one-at-a-time. Failures are returned inline (as ``BaseException``
        entries) rather than aborting the whole batch.

        Args:
            items: List of ``(title, content)`` tuples to analyze.
            categories: Optional list of supported category names; when omitted
                the analyzer falls back to the DB's active categories (or the
                built-in defaults).
            max_concurrency: Maximum number of LLM calls to run at once.

        Returns:
            A list aligned with ``items``: a ``ContentResponse`` per successful
            item, or the exception raised for that item.
        """
        if not items:
            return []

        category_str = self._build_category_string(categories)
        chain = self.prompt | self._ensure_llm() | self.parser

        inputs = [
            {
                "title": title,
                "content": content,
                "categories": category_str,
                "format_instructions": self.parser.get_format_instructions(),
            }
            for title, content in items
        ]

        logger.info(
            "Analyzing batch of %s items (max_concurrency=%s)",
            len(items),
            max_concurrency,
        )
        results = await chain.abatch(
            inputs,
            config={"max_concurrency": max_concurrency},
            return_exceptions=True,
        )
        logger.info("Batch analysis complete: %s items processed", len(results))
        return results

# Importing this module must not require an OpenAI key: the API can still run
# without analysis configured. Pass an explicit key (or set OPENAI_API_KEY) to
# construct a fully-initialized instance; process_content() will raise a clear
# error if no key is available.
def _create_analyzer() -> ContentAnalyzer:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.warning(
            "OPENAI_API_KEY is not set - ContentAnalyzer will be unavailable "
            "until a key is provided via the environment or the constructor"
        )
    return ContentAnalyzer(api_key=api_key)


ContentAnalyzerInstance = _create_analyzer()

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
