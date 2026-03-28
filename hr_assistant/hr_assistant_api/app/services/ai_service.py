"""OpenAI-powered AI service for the HR Assistant."""

import logging
from typing import Generator, List, Optional

from openai import OpenAI

from app.services.vector_store import VectorStoreService

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a helpful and knowledgeable HR Assistant for a company.
You have access to the company's HR policies and employee information.

Your responsibilities include:
- Answering questions about HR policies (leave, expenses, benefits, onboarding)
- Helping employees understand their entitlements
- Guiding employees through processes for submitting leave requests and expense claims
- Providing information about onboarding tasks and company benefits

Guidelines:
- Always be professional, empathetic, and concise
- Base your answers on the provided HR policy context when available
- If you are unsure, advise the employee to contact the HR department directly
- Do not invent policies or figures; stick to what is in the context
- For sensitive matters such as disciplinary issues, recommend speaking with HR in person
"""


class AIService:
    """Wraps the OpenAI client and ChromaDB to provide HR-aware chat responses.

    Attributes:
        client: OpenAI client instance.
        vector_store: Vector store service for policy retrieval.
        model: GPT model identifier to use for completions.
    """

    def __init__(
        self,
        openai_api_key: str,
        vector_store: VectorStoreService,
        model: str = "gpt-4",
    ) -> None:
        self.client = OpenAI(api_key=openai_api_key)
        self.vector_store = vector_store
        self.model = model

    def _get_policy_context(self, question: str, n_results: int = 5) -> str:
        """Retrieve relevant policy chunks from ChromaDB and format them.

        Args:
            question: The user's question.
            n_results: How many policy chunks to include.

        Returns:
            Formatted context string, or an empty string if nothing is found.
        """
        chunks = self.vector_store.query(question, n_results=n_results)
        if not chunks:
            return ""
        return "\n\n---\n\n".join(chunks)

    def _build_messages(
        self,
        question: str,
        employee_context: Optional[str] = None,
        conversation_history: Optional[List[dict]] = None,
    ) -> List[dict]:
        """Build the messages list for the ChatCompletion call.

        Args:
            question: Latest user message.
            employee_context: Optional string describing the current employee.
            conversation_history: Previous turns as a list of {role, content} dicts.

        Returns:
            List of message dicts ready for the OpenAI API.
        """
        policy_context = self._get_policy_context(question)

        system_content = SYSTEM_PROMPT
        if policy_context:
            system_content += f"\n\nRelevant HR Policy Context:\n{policy_context}"
        if employee_context:
            system_content += f"\n\nCurrent Employee Context:\n{employee_context}"

        messages: List[dict] = [{"role": "system", "content": system_content}]

        if conversation_history:
            messages.extend(conversation_history[-10:])  # Keep last 10 turns

        messages.append({"role": "user", "content": question})
        return messages

    def generate_response(
        self,
        question: str,
        employee_context: Optional[str] = None,
        conversation_history: Optional[List[dict]] = None,
    ) -> str:
        """Generate a complete (non-streaming) HR assistant response.

        Args:
            question: The employee's question.
            employee_context: Optional serialised employee info.
            conversation_history: Optional prior conversation turns.

        Returns:
            Assistant reply as a plain string.
        """
        messages = self._build_messages(question, employee_context, conversation_history)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.3,
            max_tokens=1024,
        )
        return response.choices[0].message.content.strip()

    def stream_response(
        self,
        question: str,
        employee_context: Optional[str] = None,
        conversation_history: Optional[List[dict]] = None,
    ) -> Generator[str, None, None]:
        """Stream an HR assistant response token-by-token.

        Yields individual token strings as they arrive from the OpenAI API.

        Args:
            question: The employee's question.
            employee_context: Optional serialised employee info.
            conversation_history: Optional prior conversation turns.

        Yields:
            Successive token strings.
        """
        messages = self._build_messages(question, employee_context, conversation_history)

        stream = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.3,
            max_tokens=1024,
            stream=True,
        )

        for chunk in stream:
            delta = chunk.choices[0].delta
            if delta.content:
                yield delta.content

    def answer_leave_question(self, question: str, employee_name: str) -> str:
        """Specialised helper for leave-related questions.

        Args:
            question: The leave-related question.
            employee_name: Full name of the employee asking.

        Returns:
            Assistant reply.
        """
        context = f"Employee name: {employee_name}"
        enriched = f"Leave-related question: {question}"
        return self.generate_response(enriched, employee_context=context)

    def answer_expense_question(self, question: str, employee_name: str) -> str:
        """Specialised helper for expense-related questions.

        Args:
            question: The expense-related question.
            employee_name: Full name of the employee asking.

        Returns:
            Assistant reply.
        """
        context = f"Employee name: {employee_name}"
        enriched = f"Expense claim question: {question}"
        return self.generate_response(enriched, employee_context=context)

    def answer_onboarding_question(self, question: str, employee_name: str) -> str:
        """Specialised helper for onboarding-related questions.

        Args:
            question: The onboarding-related question.
            employee_name: Full name of the employee asking.

        Returns:
            Assistant reply.
        """
        context = f"Employee name: {employee_name}"
        enriched = f"Onboarding question: {question}"
        return self.generate_response(enriched, employee_context=context)
