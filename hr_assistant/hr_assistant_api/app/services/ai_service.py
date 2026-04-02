"""OpenAI-powered AI service for the HR Assistant using RAG template."""

import logging
from typing import Generator, List, Optional

from openai import OpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI

from app.services.vector_store import VectorStoreService
from app.config import settings

logger = logging.getLogger(__name__)

# RAG Template for HR Assistant
RAG_TEMPLATE = """You are an HR assistant.

Your job is to answer user questions using the provided context and conversation history.

--------------------------------
OUTPUT MODE PRIORITY (highest to lowest):
1. TREE / ORG STRUCTURE MODE
2. TABLE MODE
3. TEXT MODE
--------------------------------

DATA SOURCE PRIORITY:
1. Use the retrieved context as the primary source of truth
2. If not found, use conversation history ONLY if it was previously derived from context
3. If not found in either, you may use general HR knowledge but clearly indicate it

--------------------------------
STRICT RULES:
- Do NOT hallucinate specific details (dates, amounts, policies) not in context
- Do NOT infer missing values
- If data is missing, use "" (empty string)
- Keep answers concise and factual
- If using general knowledge, say "Based on general HR practices..."
- IMPORTANT: If you provide organizational information, preserve structure

--------------------------------
TREE / ORG STRUCTURE OUTPUT MODE (STRICT OVERRIDE):

Trigger this mode when the question is about:
- organizational structure
- org structure
- org chart
- hierarchy
- reporting structure
- who reports to whom
- team structure
- chain of command
- management structure

If triggered:
- This mode OVERRIDES all other modes
- You MUST return ONLY a tree structure
- DO NOT return paragraphs, explanations, or JSON

CRITICAL FORMATTING RULES:
- Each node MUST be on a NEW LINE
- Output MUST contain real line breaks (not spaces)
- DO NOT compress output into a single line
- Use plain text only

FORMAT:
Parent
├── Child
│   ├── Sub-child
│   └── Sub-child
└── Child

- Maintain proper indentation using spaces
- Use characters: ├── , └── , │

DATA HANDLING:
- The context may be unordered or not perfectly structured
- You MUST reconstruct the hierarchy logically from the available data
- Do NOT fall back to paragraph format
- If only partial hierarchy is available, construct the best possible structure

VALIDATION BEFORE RETURN:
- Ensure output has multiple lines
- If output is a single line, rewrite into proper multi-line tree format

FAILURE CONDITION:
If no hierarchy information is available, return:
"I don't have enough information to determine the organizational structure."

--------------------------------
TABLE OUTPUT MODE:

Trigger this mode when:
- User explicitly asks for table, list, or structured format
- OR user asks to reformat previous answer into table/list

If triggered:
- Return ONLY valid JSON
- Do NOT include ANY text before or after JSON

FORMAT:
{{
  "columns": ["column1", "column2"],
  "rows": [
    ["value1", "value2"]
  ]
}}

JSON RULES:
- Columns must match row values exactly
- No extra fields
- No markdown
- Use "" for missing values

If no data is available, return:
{{
  "columns": [],
  "rows": []
}}

--------------------------------
NON-TABLE / TEXT OUTPUT MODE:

- Return a clear natural language answer
- Do NOT include JSON
- If no answer found in context, you may provide general guidance but clearly state it

--------------------------------

IMPORTANT:
- NEVER mix JSON and text in the same response
- NEVER generate partial JSON
- Follow output mode priority strictly

--------------------------------

Employee Context:
{employee_context}

NOTE: If hire date is provided above (e.g., "Hire Date: 06/30/2021"), use this exact format in your response. Do not convert to other date formats.

Conversation History:
{history}

Relevant Context:
{context}

Current Question:
{question}

Answer:
"""


class AIService:
    """Wraps the OpenAI client and ChromaDB to provide HR-aware chat responses.

    Attributes:
        client: OpenAI client instance.
        vector_store: Vector store service for policy retrieval.
        model: GPT model identifier to use for completions.
        rag_chain: LangChain RAG chain for generating responses.
    """

    def __init__(
        self,
        openai_api_key: str,
        vector_store: VectorStoreService,
        model: Optional[str] = None,
    ) -> None:
        self.client = OpenAI(api_key=openai_api_key)
        self.vector_store = vector_store
        self.model = model or settings.OPENAI_MODEL_NAME
        
        # Initialize LangChain components
        self.llm = ChatOpenAI(
            temperature=0.3,
            model_name=self.model,
            openai_api_key=openai_api_key
        )
        
        # Create RAG prompt template
        self.rag_prompt = ChatPromptTemplate.from_template(RAG_TEMPLATE)
        
        # Create retriever from vector store
        self.retriever = self.vector_store.vector_store.as_retriever(
            search_kwargs={"k": 5}
        )

    def generate_response(
        self,
        question: str,
        employee_context: Optional[str] = None,
        conversation_history: Optional[List[dict]] = None,
    ) -> str:
        try:
            logger.info(f"Received question: {question}")
            
            # Format conversation history with clear labels
            history_text = ""
            if conversation_history:
                # Take last 5 turns to avoid context overflow
                recent_history = conversation_history[-5:]
                history_parts = []
                for i, msg in enumerate(recent_history):
                    role = "USER" if msg["role"] == "user" else "ASSISTANT"
                    history_parts.append(f"[{role}]: {msg['content']}")
                history_text = "\n".join(history_parts)
            
            # Check if the user is asking for a table format
            table_keywords = ["table", "put in a table", "show as a table", "display as table", "format as table"]
            tree_keywords = ["organizational structure", "org structure", "org chart", "hierarchy", "reporting structure", "who reports to whom", "team structure", "chain of command", "management structure", "tree", "tree format", "tree diagram"]
            
            is_table_request = any(keyword in question.lower() for keyword in table_keywords)
            is_tree_request = any(keyword in question.lower() for keyword in tree_keywords)
            
            logger.info(f"Is table request: {is_table_request}")
            logger.info(f"Is tree request: {is_tree_request}")
            
            # Retrieve context
            try:
                context_docs = self.retriever.invoke(question)
                context = "\n\n---\n\n".join([doc.page_content for doc in context_docs])
                logger.info(f"Retrieved {len(context_docs)} context documents")
                if context_docs:
                    logger.info(f"First context doc preview: {context_docs[0].page_content[:200]}...")
                else:
                    logger.warning("No context documents retrieved!")
            except Exception as e:
                logger.error(f"Error retrieving context: {e}")
                context = ""
            
            # Create the input for the prompt
            chain_input = {
                "question": question,
                "history": history_text,
                "context": context,
                "employee_context": employee_context or ""
            }
            
            # Log the employee context specifically
            if employee_context:
                logger.info(f"Employee context found: {employee_context}")
                # Check if this is an employment status question
                if any(keyword in question.lower() for keyword in ["still working", "currently employed", "still employed", "working with", "employment status"]):
                    logger.info("This appears to be an employment status question - check the status in the context above")
            else:
                logger.warning("No employee context provided - employee may not be found in database")
            
            logger.info("Invoking RAG prompt...")
            
            # Invoke the chain step by step
            try:
                # Format the prompt
                formatted_prompt = self.rag_prompt.format(**chain_input)
                logger.info(f"Prompt formatted successfully, length: {len(formatted_prompt)}")
                
                # Get LLM response
                response = self.llm.invoke(formatted_prompt)
                logger.info(f"LLM response received: {str(response)[:200]}...")
                
                # Parse the response
                final_response = StrOutputParser().invoke(response)
                logger.info(f"Final response: {final_response[:200]}...")
                
            except Exception as e:
                logger.error(f"Error in RAG chain: {e}", exc_info=True)
                raise
            
            # If it's a table request (not tree), validate the JSON response
            if is_table_request and not is_tree_request:
                logger.info(f"Checking if table response is valid JSON...")
                logger.info(f"Response starts with: {final_response[:50]}...")
                
                # Check if response looks like JSON
                stripped = final_response.strip()
                if not (stripped.startswith('{') and stripped.endswith('}')):
                    logger.warning("Response doesn't look like JSON, returning as-is")
                    # Not JSON, return as regular text
                    return final_response
                
                try:
                    import json
                    parsed = json.loads(final_response)
                    if not isinstance(parsed, dict) or 'columns' not in parsed or 'rows' not in parsed:
                        logger.error("Response is JSON but not valid table format")
                        logger.info(f"Parsed keys: {list(parsed.keys()) if isinstance(parsed, dict) else 'Not a dict'}")
                        return json.dumps({
                            "columns": ["Error"],
                            "rows": [["Invalid table format received from AI. Please try again."]]
                        })
                    logger.info("Valid JSON table format confirmed")
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse table response as JSON: {e}")
                    logger.info(f"Response content: {final_response}")
                    # Return the original response if it's not valid JSON
                    return final_response
            
            return final_response
            
        except Exception as e:
            logger.error(f"Failed to generate response: {e}", exc_info=True)
            return "I apologize, but I encountered an error while processing your request. Please try again or contact HR directly."

    def stream_response(
        self,
        question: str,
        employee_context: Optional[str] = None,
        conversation_history: Optional[List[dict]] = None,
    ) -> Generator[str, None, None]:
        """Stream a response to a user's question.

        Args:
            question: The user's question.
            employee_context: Optional employee information.
            conversation_history: Previous conversation turns.

        Yields:
            Response tokens as they are generated.
        """
        try:
            # For now, use the regular generate_response and stream the result
            # Could be enhanced with true streaming later
            response = self.generate_response(question, employee_context, conversation_history)
            for word in response.split():
                yield word + " "
                
        except Exception as e:
            logger.error(f"Failed to stream response: {e}")
            yield "I apologize, but I encountered an error while processing your request. Please try again or contact HR directly."
