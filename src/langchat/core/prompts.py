# Copyright (c) 2025 NeuroBrain Co Ltd.
# Licensed under the MIT License.

import warnings
from typing import List, Optional, Tuple

try:
    from langchain_core.prompts import PromptTemplate
except ImportError:
    from langchain.prompts import PromptTemplate  # type: ignore

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
    llm,
    custom_prompt: Optional[str] = None,
    verbose_chains: bool = False,
) -> str:
    """
    Generate standalone question from query and chat history.

    Args:
        query: User query
        chat_history: List of (query, response) tuples
        llm: LLM provider instance
        custom_prompt: Custom prompt template (optional)
        verbose_chains: Verbose mode

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

    # Provider-agnostic invocation: call the configured LLM directly.
    try:
        from langchain_core.messages import HumanMessage
    except ImportError:
        from langchain.schema import HumanMessage  # type: ignore[no-redef]

    formatted_prompt = prompt.format(question=query, chat_history=formatted_chat_history)
    result = await llm.ainvoke([HumanMessage(content=formatted_prompt)])

    return result.strip() if isinstance(result, str) else query.strip()
