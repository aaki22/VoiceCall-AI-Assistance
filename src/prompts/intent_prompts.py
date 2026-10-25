from langchain_core.prompts import ChatPromptTemplate


TRAFFIC_INTENT_PROMPT = ChatPromptTemplate.from_template(
    """
Detect if the user is asking about traffic.

Return JSON only.

Examples:
User: traffic from chennai airport to t nagar
{{"intent":"traffic","start":"Chennai Airport","end":"T Nagar"}}

User: traffic in guindy
{{"intent":"traffic","start":"Guindy","end":"Guindy"}}

User: hello
{{"intent":"other","start":"","end":""}}

User input: {user_text}
"""
)


ASSISTANT_INTENT_PROMPT = ChatPromptTemplate.from_template(
    """
You are an intent classifier for a phone AI assistant.

Return JSON only.

Possible intents:
1. tamil_nadu_news
2. general_chat

User input: {user_text}

Output format:
{{"intent": ""}}
"""
)
