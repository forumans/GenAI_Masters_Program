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
RESPONSE FORMAT (REQUIRED):
ALWAYS return output in this JSON format (no markdown, no code blocks):

{{"type": "text | table | tree | metric", "data": ..., "meta": {{"title": "", "description": ""}}}}

CRITICAL: 
- Return ONLY the JSON object
- DO NOT wrap in ```json``` or any markdown
- DO NOT add any text before or after the JSON
- The entire response must be valid JSON

RULES:
- Do NOT return raw text outside JSON
- Select correct type based on user intent:
  * For org structure → type = "tree"
  * For tabular data → type = "table"
  * For counts/summary → type = "metric"
  * Otherwise → type = "text"
- For tree type: data should be a string with line breaks
- For table type: data should be {{ "columns": [...], "rows": [...] }}
- For metric type: data should be {{ "label": string, "value": number }}
- For text type: data should be a string

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
TREE STRUCTURE HANDLING:
When user asks about organizational structure:
- Return type: "tree"
- Data: String with proper tree format using ├──, └──, │
- Example data: "Board of Directors\\n└── CEO\\n    ├── CFO\\n    └── HR"
- Each level must be on a new line

--------------------------------
TABLE STRUCTURE HANDLING:
When user asks for tabular data:
- Return type: "table"
- Data: Object with columns and rows arrays
- Example data: {{ "columns": ["Name", "Date"], "rows": [["John", "01/01/2023"]] }}

--------------------------------
METRIC STRUCTURE HANDLING:
When user asks for counts or summaries:
- Return type: "metric"
- Data: Object with label and value
- Example data: {{ "label": "Total Employees", "value": 124 }}

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
            
            # Check if the user is asking for a table format (kept for logging only)
            table_keywords = ["table", "put in a table", "show as a table", "display as table", "format as table"]
            tree_keywords = ["organizational structure", "org structure", "org chart", "hierarchy", "reporting structure", "who reports to whom", "team structure", "chain of command", "management structure", "tree", "tree format", "tree diagram"]
            
            is_table_request = any(keyword in question.lower() for keyword in table_keywords)
            is_tree_request = any(keyword in question.lower() for keyword in tree_keywords)
            
            logger.info(f"Request type - Table: {is_table_request}, Tree: {is_tree_request}")
            
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
            
            # Parse and validate JSON response
            try:
                import json
                import re
                
                # Try to extract JSON from markdown code blocks if present
                json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', final_response, re.DOTALL)
                if json_match:
                    final_response = json_match.group(1)
                elif final_response.strip().startswith('```'):
                    # Remove any markdown wrapper
                    lines = final_response.strip().split('\n')
                    if lines[0].startswith('```'):
                        lines = lines[1:]
                    if lines[-1].endswith('```'):
                        lines = lines[:-1]
                    final_response = '\n'.join(lines).strip()
                
                parsed_response = json.loads(final_response)
                
                # Validate required fields
                if not isinstance(parsed_response, dict) or 'type' not in parsed_response or 'data' not in parsed_response:
                    logger.error("Invalid JSON structure from LLM")
                    logger.info(f"Response: {final_response}")
                    # Return fallback response
                    return json.dumps({
                        "type": "text",
                        "data": "I received an invalid response format. Please try again.",
                        "meta": { "title": "Error" }
                    })
                
                # Validate type
                valid_types = ["text", "table", "tree", "metric"]
                if parsed_response['type'] not in valid_types:
                    logger.error(f"Invalid type: {parsed_response['type']}")
                    # Fallback to text
                    parsed_response['type'] = 'text'
                    parsed_response['data'] = str(parsed_response.get('data', ''))
                
                # Return valid JSON
                return json.dumps(parsed_response)
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                logger.info(f"Raw response: {final_response}")
                # Return as text if JSON parsing fails
                return json.dumps({
                    "type": "text",
                    "data": final_response,
                    "meta": { "title": "Response" }
                })
            
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
