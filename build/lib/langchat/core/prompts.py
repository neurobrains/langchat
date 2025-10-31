"""
Prompt templates and question generation utilities.
"""

from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from typing import List, Tuple, Optional

from langchat.adapters.services.openai_service import OpenAILLMService


def create_standalone_question_prompt(custom_prompt: Optional[str] = None) -> PromptTemplate:
    """
    Create prompt template for generating standalone questions.
    
    Args:
        custom_prompt: Custom prompt template (optional)
    
    Returns:
        PromptTemplate instance
    """
    default_template = """
    Given the user's follow-up question, which may be written in Bangla phonetic, Bangla, or English, and the previous conversation history, rewrite the user's follow-up question into a standalone query in English. Ensure the query includes enough context to be understood without the previous messages. The goal is to create a precise query to retrieve relevant information from the vector store. Make sure the query is concise but complete.
    Please don't rephrase hi, hello, hey, thank you, whatsup or similar greetings. Please keep them as is.
    
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
    custom_prompt: Optional[str] = None
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
    
    # Create prompt
    prompt = create_standalone_question_prompt(custom_prompt=custom_prompt)
    
    # Use standalone LLM for question generation (can use a simpler/cheaper model)
    # OpenAI service
    if not hasattr(llm, 'current_key') or not llm.current_key:
        raise ValueError("No API key available for standalone question generation")
    
    standalone_llm = ChatOpenAI(
        model=llm.model,
        temperature=llm.temperature,
        openai_api_key=llm.current_key,
        max_retries=1
    )
    
    # Create chain
    chain = LLMChain(
        llm=standalone_llm,
        prompt=prompt,
        output_key="standalone_question",
        verbose=True
    )
    
    # Generate standalone question
    result = await chain.ainvoke({
        "question": query,
        "chat_history": formatted_chat_history
    })
    
    return result.get("standalone_question", query).strip()