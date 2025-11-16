"""
Prompt templates and question generation utilities.
"""

import warnings
from typing import List, Optional, Tuple, cast

from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from langchat.adapters.services.openai_service import OpenAILLMService

# Suppress warnings before importing langchain
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", message=".*deprecated.*")


def create_standalone_question_prompt(
    custom_prompt: Optional[str] = None,
) -> PromptTemplate:
    """
    Create prompt template for generating standalone questions.

    Args:
        custom_prompt: Custom prompt template (optional)

    Returns:
        PromptTemplate instance
    """
    default_template = """Given the following conversation and a follow up input, rephrase the follow up input to be a standalone question or a statement. Strictly generate standalone question in English language only.

    Please don't rephrase hi, hello, hey, whatsup or similar greetings. Please keep them as is.

    Chat History:
    {chat_history}

    Follow Up Input: {question}
    Standalone question:"""

    template = custom_prompt if custom_prompt else default_template
    return PromptTemplate.from_template(template)


async def generate_standalone_question(
    query: str,
    chat_history: List[Tuple[str, str]],
    llm: OpenAILLMService,
    custom_prompt: Optional[str] = None,
    verbose_chains: bool = False,
) -> str:
    """
    Generate standalone question from query and chat history.

    Args:
        query: User query
        chat_history: List of (query, response) tuples
        llm: LLM provider instance

    Returns:
        Standalone question string
    """
    # Format chat history
    formatted_chat_history = "\n".join([f"Human: {q}\nAI: {a}" for q, a in chat_history])

    # Show verbose output if enabled (to debug chat_history)
    if verbose_chains:
        from rich.console import Console
        from rich.panel import Panel

        console = Console()
        console.print()
        console.print(
            Panel(
                f"Chat History Entries: {len(chat_history)}\n\nFormatted Chat History:\n{formatted_chat_history}",
                title="[bold yellow]STANDALONE QUESTION CHAIN - Chat History[/bold yellow]",
                title_align="left",
                border_style="yellow",
                padding=(1, 2),
            )
        )
        console.print()

    # Create prompt
    prompt = create_standalone_question_prompt(custom_prompt=custom_prompt)

    # Use standalone LLM for question generation (can use a simpler/cheaper model)
    # OpenAI service
    if not hasattr(llm, "current_key") or not llm.current_key:
        raise ValueError("No API key available for standalone question generation")

    standalone_llm = ChatOpenAI(
        model=llm.model,
        temperature=llm.temperature,
        openai_api_key=llm.current_key,  # type: ignore[call-arg]
        max_retries=1,
    )

    # Create chain with verbose based on config
    chain = LLMChain(
        llm=standalone_llm,
        prompt=prompt,
        output_key="standalone_question",
        verbose=verbose_chains,
    )

    # Generate standalone question
    result = await chain.ainvoke({"question": query, "chat_history": formatted_chat_history})

    standalone_question = result.get("standalone_question", query)
    return (
        cast("str", standalone_question).strip()
        if isinstance(standalone_question, str)
        else query.strip()
    )
