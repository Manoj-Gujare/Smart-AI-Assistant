from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.tools import Tool
from langchain.memory import ConversationBufferWindowMemory
import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

load_dotenv()

class SmartAgent:
    def __init__(self, session_id):
        self.session_id = session_id
        self.memory = ConversationBufferWindowMemory(
            return_messages=True,
            memory_key="chat_history",
            k=6
        )
        self.llm = ChatGroq(
            temperature=0.7,
            model_name="meta-llama/llama-4-scout-17b-16e-instruct",
            groq_api_key=os.getenv("GROQ_API_KEY")
        )
        self.rag_chain = None
        self.reminders = []
        self.document_processed = False  # Track document processing status
        
        # Create tools with proper binding
        self.tools = [
            Tool(
                name="document_retrieval_tool",
                func=self.rag_tool,
                description="Retrieve information from uploaded documents. Use when asked about document content."
            ),
            Tool(
                name="reminder_tool",
                func=self.reminder_tool,
                description="Set a reminder for the user. Use when asked to remember something for later."
            )
        ]
        
        self.agent = self._create_agent()
    
    def _create_agent(self):
        prompt = ChatPromptTemplate.from_messages([
            ("system", 
            "You are a helpful personal assistant. Remember the user's name and preferences. "
            "You can retrieve information from uploaded documents and set reminders. "
            "Always be friendly and engaging. When asked to summarize a document, "
            "use the document_retrieval_tool to get the content and provide a concise summary. "
            "If the user mentions an attached document, assume it has been processed and is available for querying. "
            "If the documents do not contain relevant information for the user's query, use your own general knowledge to provide a helpful and accurate response."),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])

        
        agent = create_openai_tools_agent(self.llm, self.tools, prompt)
        return AgentExecutor(agent=agent, tools=self.tools, memory=self.memory, verbose=True)
    
    def rag_tool(self, query: str) -> str:
        """Retrieve information from uploaded documents."""
        if self.rag_chain:
            logger.info(f"Document retrieval tool: Query - '{query}'")
            try:
                result = self.rag_chain.invoke({"query": query})
                return result["result"]
            except Exception as e:
                logger.error(f"Document retrieval error: {str(e)}", exc_info=True)
                return f"Error retrieving document information: {str(e)}"
        else:
            logger.warning("Document retrieval not available")
            return "No documents have been processed yet. Please upload a document first."
    
    def reminder_tool(self, reminder_text: str) -> str:
        """Set a reminder for the user."""
        self.reminders.append(reminder_text)
        return f"Reminder set: {reminder_text}"
    
    def generate_response(self, user_input):
        try:
            doc_status = "The document is available." if self.document_processed else "No document is available."
            modified_input = f"{doc_status}\n{user_input}"

            return self.agent.invoke({"input": modified_input})["output"]
        except Exception as e:
            logger.error(f"Response generation error: {str(e)}", exc_info=True)
            return "I encountered an error while processing your request. Please try again."

    
    def get_memory(self):
        return self.memory.load_memory_variables({})["chat_history"]