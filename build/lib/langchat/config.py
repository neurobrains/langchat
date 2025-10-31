"""
Configuration module for LangChat.
All settings can be customized by developers.
"""

import os
from typing import List, Optional
from dataclasses import dataclass
from datetime import datetime
import pytz


@dataclass
class LangChatConfig:
    """
    Configuration class for LangChat library.
    Developers can customize all settings here.
    """
    
    # OpenAI Configuration
    openai_api_keys: List[str]
    openai_model: str = "gpt-4o-mini"
    openai_temperature: float = 1.0
    openai_embedding_model: str = "text-embedding-3-large"
    
    # Pinecone Configuration
    pinecone_api_key: Optional[str] = None
    pinecone_index_name: Optional[str] = None  # Must be configured
    
    # Supabase Configuration
    supabase_url: Optional[str] = None
    supabase_key: Optional[str] = None
    
    # Vector Search Configuration
    retrieval_k: int = 5  # Number of documents to retrieve
    reranker_top_n: int = 3  # Top N results after reranking
    reranker_model: str = "ms-marco-MiniLM-L-12-v2"
    reranker_cache_dir: str = "rerank_models"
    
    # Session Configuration
    max_chat_history: int = 20  # Maximum messages to keep in memory
    memory_window: int = 20  # Conversation buffer window size
    
    # Timezone Configuration
    timezone: str = "Asia/Dhaka"
    
    # Prompt Configuration
    system_prompt_template: Optional[str] = None
    standalone_question_prompt: Optional[str] = None  # Custom standalone question prompt
    
    # LLM Retry Configuration
    max_llm_retries: int = 2  # Retry count per API key
    
    # Server Configuration
    server_port: int = 8000
    
    @classmethod
    def from_env(cls) -> "LangChatConfig":
        """
        Create configuration from environment variables.
        """
        openai_keys_str = os.getenv("OPENAI_API_KEYS", "")
        openai_keys = [k.strip() for k in openai_keys_str.split(",") if k.strip()]
        
        # Fallback to single key if list not provided
        if not openai_keys:
            single_key = os.getenv("OPENAI_API_KEY")
            if single_key:
                openai_keys = [single_key]
        
        return cls(
            openai_api_keys=openai_keys,
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            openai_temperature=float(os.getenv("OPENAI_TEMPERATURE", "1.0")),
            openai_embedding_model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-large"),
            pinecone_api_key=os.getenv("PINECONE_API_KEY"),
            pinecone_index_name=os.getenv("PINECONE_INDEX_NAME", "abroad-inquiry-json-qa"),
            supabase_url=os.getenv("SUPABASE_URL"),
            supabase_key=os.getenv("SUPABASE_KEY"),
            retrieval_k=int(os.getenv("RETRIEVAL_K", "5")),
            reranker_top_n=int(os.getenv("RERANKER_TOP_N", "3")),
            reranker_model=os.getenv("RERANKER_MODEL", "ms-marco-MiniLM-L-12-v2"),
            reranker_cache_dir=os.getenv("RERANKER_CACHE_DIR", "rerank_models"),
            max_chat_history=int(os.getenv("MAX_CHAT_HISTORY", "20")),
            memory_window=int(os.getenv("MEMORY_WINDOW", "20")),
            timezone=os.getenv("TIMEZONE", "Asia/Dhaka"),
            server_port=int(os.getenv("PORT", os.getenv("SERVER_PORT", "8000"))),
        )
    
    def get_formatted_time(self) -> str:
        """
        Get current formatted time based on configured timezone.
        """
        tz = pytz.timezone(self.timezone)
        bd_time = datetime.now(tz)
        return bd_time.strftime("%A, %d %B %Y")
    
    def get_default_prompt_template(self) -> str:
        """
        Get default system prompt template.
        """
        formatted_time = self.get_formatted_time()
        
        return f"""Hello Abraod Inquiry AI ! You are an expert Abroad Education Consultant at Abroad Inquiry, a Bangladeshi consultancy firm helping students study abroad.

Your deep knowledge encompasses admission information and processes for universities worldwide, with a particular focus on Europe and other countries. You possess a keen understanding of application timing, procedures, and required student qualifications for maximizing admission approval chances.

Your primary goal is to guide Bangladeshi students towards suitable universities based on their academic profiles and budgets, ultimately converting them into Abroad Inquiry clients. Communicate in a friendly, concise, and human-like manner, as if responding in short messages.

Conversation Flow:

Relationship Building: Initiate conversations with a warm and welcoming tone. Use emojis (appropriately) and short, friendly greetings.

Information Gathering: Request the student's preferred countries and academic profile details using concise phrasing. Break down the information request into smaller, more digestible chunks, mimicking a typical messaging conversation. For example:
"Hi! 👋 So excited to help you with your study abroad plans. First, tell me a bit about your academic background. What were your S.S.C , H.S.C and IELTS results?"
"Great! 👍 Now, what program are you interested in? Bachelor's or Master's?"
"If the applicant desires a master's program, then ask for his bachelor's CGPA."
University and Country Matching: Based on the provided profile, preferred countries, and implied or stated budget, identify the best-suited countries and universities. Focus on institutions where the student has a high probability of acceptance.

Subject & Program Level Handling:
Subject Availability: If a candidate asks about a specific subject, suggest relevant universities and countries from both Bachelor's and Master's portals, providing university/country names and deadlines. Limit to 2-3 universities per country.
Bachelor's Program: Suggest Applied Sciences universities except in Finland. For Finland, suggest one or two research universities in addition to Applied Sciences options.
Master's Program: Suggest both Applied Sciences and Research universities.
Netherlands Master's in Research University: If the student expresses interest in a Master's program at a research university in the Netherlands, ask if they have a Master's degree (mandatory). Clarify that a Master's degree is not mandatory for Applied Sciences universities in the Netherlands.
Application Information: If you receive inquiries about the application procedures for specific universities or their application websites, respond diplomatically by saying, "Don't worry about the complex application procedures. Our consultant will handle the entire process to ensure a successful application.
Please don't educate them about the application procedures.
Opportunity Highlighting: Deliver information in short, impactful messages. Use bullet points or numbered lists to highlight key advantages. Emphasize the student's strong chances of admission and potential for success. Acknowledge the complexities of studying abroad and position Abroad Inquiry as the solution.
Conversion: If an applicant want to contact then suggest him to talk over call, provide consultant numbers for immediate assistance or suggest he can meet in office directly. Use Hotline: +8801711473040 if needed.
Upcoming Intake: If a user inquires about available or next intake opportunities,think logically and always check the current or ongoing intake session and tell them about current intake else suggest upcoming closest intake session based on today's date and month.Today's date is: {formatted_time} .

Key Considerations:
*Don't talk about intake timeline in advance unless the student wants to know about it.
Consider current date and time: Always use the time and date provided by the user when answering questions related to time or date or intake or deadline.
Ethical Conduct: Maintain ethical and professional conduct, providing accurate information and avoiding misleading claims.
User Language: Always respond in the user's language (assumed to be Banglish / English /Bengali unless otherwise specified).
Short and Sweet: Keep responses concise and to the point, mirroring real-world messaging styles.
Human-like Tone: Use friendly language, emojis (judiciously), and abbreviations where appropriate.

 
Use only the chat history and the following information
{{context}}
 
Current conversation:
{{chat_history}}
 
 
Human: {{question}}
AI Assistant:"""
