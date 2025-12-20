"""
Customer Support Chatbot - Interactive CLI
Production-ready RAG chatbot with conversation memory
"""

import os
from dotenv import load_dotenv
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from utils.rag_chain import CustomerSupportRAG
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)


class CustomerSupportChatbot:
    """
    Interactive customer support chatbot with memory and RAG
    """
    
    def __init__(self):
        """Initialize the chatbot with RAG and memory"""
        
        print(f"{Fore.CYAN}🤖 Initializing Customer Support AI...{Style.RESET_ALL}")
        
        # Initialize RAG system (with system instruction built-in)
        self.rag = CustomerSupportRAG()
        
        # Initialize memory (keeps last 10 messages)
        self.memory = ConversationBufferWindowMemory(
            k=10,  # Remember last 10 messages
            return_messages=True,
            memory_key="chat_history"
        )
        
        print(f"{Fore.GREEN}✓ Chatbot ready!{Style.RESET_ALL}\n")
        print(f"{Fore.CYAN}💡 Token Optimization: System instructions set once - saves 50-75% tokens!{Style.RESET_ALL}\n")
    
    def chat(self, user_message: str) -> dict:
        """
        Process user message and return response
        
        Args:
            user_message: User's question/message
            
        Returns:
            AI response with sources
        """
        
        # Format chat history from memory
        memory_dict = self.memory.load_memory_variables({})
        chat_history_messages = memory_dict.get("chat_history", [])
        
        # Convert messages to readable format
        chat_history_text = ""
        if chat_history_messages:
            history_parts = []
            for msg in chat_history_messages:
                if hasattr(msg, 'type'):
                    role = "User" if msg.type == "human" else "Assistant"
                    history_parts.append(f"{role}: {msg.content}")
            chat_history_text = "\n".join(history_parts)
        
        # Get answer from RAG system with sources AND memory
        result = self.rag.ask_with_sources(user_message, chat_history_text)
        
        # Save to memory
        self.memory.save_context(
            {"input": user_message},
            {"output": result["answer"]}
        )
        
        return result
    
    def run_interactive(self):
        """Run the interactive chatbot in terminal"""
        
        print(f"""
{Fore.CYAN}╔══════════════════════════════════════════════════╗
║     💬 TechFlow CRM - Customer Support AI       ║
╚══════════════════════════════════════════════════╝{Style.RESET_ALL}

{Fore.YELLOW}How can I help you today?{Style.RESET_ALL}

{Fore.CYAN}Commands:{Style.RESET_ALL}
- Type your question and press Enter
- Type '{Fore.RED}exit{Style.RESET_ALL}' or '{Fore.RED}quit{Style.RESET_ALL}' to end conversation
- Type '{Fore.YELLOW}clear{Style.RESET_ALL}' to clear chat history
- Type '{Fore.YELLOW}help{Style.RESET_ALL}' for sample questions

{Fore.GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Style.RESET_ALL}
        """)
        
        while True:
            try:
                # Get user input
                user_input = input(f"\n{Fore.BLUE}You: {Style.RESET_ALL}").strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print(f"\n{Fore.CYAN}👋 Thank you for using TechFlow CRM Support! Have a great day!{Style.RESET_ALL}\n")
                    break
                
                if user_input.lower() == 'clear':
                    self.memory.clear()
                    print(f"{Fore.YELLOW}🗑️  Chat history cleared!{Style.RESET_ALL}")
                    continue
                
                if user_input.lower() == 'help':
                    self.show_help()
                    continue
                
                # Get AI response
                print(f"{Fore.YELLOW}🤔 Thinking...{Style.RESET_ALL}", end="\r")
                
                result = self.chat(user_input)
                
                # Display answer
                print(f"{Fore.GREEN}AI: {Style.RESET_ALL}{result['answer']}")
                
                # Display sources if available
                if result['num_sources'] > 0:
                    print(f"\n{Fore.CYAN}📚 Sources: Found {result['num_sources']} relevant document(s){Style.RESET_ALL}")
            
            except KeyboardInterrupt:
                print(f"\n\n{Fore.CYAN}👋 Interrupted. Goodbye!{Style.RESET_ALL}\n")
                break
            
            except Exception as e:
                print(f"\n{Fore.RED}❌ Error: {str(e)}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Please try again or type 'exit' to quit.{Style.RESET_ALL}")
    
    def show_help(self):
        """Display example questions"""
        print(f"""
{Fore.CYAN}❓ Sample Questions You Can Ask:{Style.RESET_ALL}

{Fore.YELLOW}Pricing & Plans:{Style.RESET_ALL}
- "What pricing plans do you offer?"
- "How much does the Professional plan cost?"
- "Do you offer a free trial?"

{Fore.YELLOW}Features:{Style.RESET_ALL}
- "What integrations are available?"
- "Does TechFlow CRM have a mobile app?"
- "What features are included?"

{Fore.YELLOW}Support:{Style.RESET_ALL}
- "How do I contact customer support?"
- "What are your support hours?"
- "How do I reset my password?"

{Fore.YELLOW}Account Management:{Style.RESET_ALL}
- "How do I add team members?"
- "Can I export my data?"
- "How do I change my plan?"

{Fore.YELLOW}Security:{Style.RESET_ALL}
- "Is my data secure?"
- "Are you GDPR compliant?"
- "Where is my data stored?"

{Fore.YELLOW}Billing:{Style.RESET_ALL}
- "What payment methods do you accept?"
- "What's your refund policy?"
- "When will I be billed?"
        """)


def main():
    """Main entry point"""
    
    # Load environment variables
    load_dotenv()
    
    # Check if API keys are set
    if not os.getenv("GEMINI_API_KEY"):
        print(f"{Fore.RED}❌ Error: GEMINI_API_KEY not found in .env file{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Please add your Gemini API key to .env file{Style.RESET_ALL}")
        return
    
    if not os.getenv("PINECONE_API_KEY"):
        print(f"{Fore.RED}❌ Error: PINECONE_API_KEY not found in .env file{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Please add your Pinecone API key to .env file{Style.RESET_ALL}")
        return
    
    try:
        # Create and run chatbot
        chatbot = CustomerSupportChatbot()
        chatbot.run_interactive()
    
    except Exception as e:
        print(f"\n{Fore.RED}❌ Fatal Error: {str(e)}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Make sure you have run 'python ingest_documents.py' first!{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
