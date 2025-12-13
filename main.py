"""
Personal Information Assistant - Main Entry Point
"""

import os
import sys
import logging
from pathlib import Path

from assistant import HybridAssistant
from config import Config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_banner():
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
                                                                   
             PERSONAL INFORMATION ASSISTANT                    
                                                                   
         • PDF Processing with OCR Support                         
         • Knowledge Base (RAG)                                    
         • General Questions Support                               
                                                                   
    ╚═══════════════════════════════════════════════════════════════╝
    """)


def print_help():
    print("""
     COMMANDS:
    ─────────────────────────────────────────────────────────────────
    quit / exit          - Exit the assistant
    clear               - Clear conversation history
    stats               - Show assistant statistics
    add <filepath>      - Add new PDF to knowledge base
    search <query>      - Search knowledge base
    kb <question>       - Force answer from knowledge base only
    general <question>  - Force general answer (ignore KB)
    rebuild             - Rebuild knowledge base from scratch
    help                - Show this help message
    ─────────────────────────────────────────────────────────────────
    """)


def choose_provider() -> str:
    """Let user choose LLM provider"""
    print("\n🤖 Select LLM Provider:")
    print("  1. Cohere (Free - Fast)")
    print("  2. Groq (Free - Fast)")
    print("  3. OpenAI (Paid - Best)")
    
    choice = input("\nChoice [1]: ").strip() or "1"
    
    providers = {"1": "cohere", "2": "groq", "3": "openai"}
    return providers.get(choice, "cohere")


def run_cli():
    """Run interactive CLI"""
    print_banner()
    
    # Choose provider
    provider = choose_provider()
    
    # Check API key
    key_map = {
        "cohere": ("COHERE_API_KEY", Config.COHERE_API_KEY),
        "groq": ("GROQ_API_KEY", Config.GROQ_API_KEY),
        "openai": ("OPENAI_API_KEY", Config.OPENAI_API_KEY)
    }
    
    key_name, key_value = key_map[provider]
    if not key_value:
        print(f"\n {key_name} not found in .env file!")
        print(f"   Add {key_name}=your-key to .env file")
        return
    
    # Initialize assistant
    print(f"\n Initializing with {provider.upper()}...\n")
    
    assistant = HybridAssistant(llm_provider=provider)
    
    # Check if rebuild needed
    rebuild = input("Rebuild knowledge base? (y/N): ").strip().lower() == 'y'
    assistant.initialize(force_rebuild=rebuild)
    
    # Print help
    print_help()
    
    # Main loop
    while True:
        try:
            user_input = input("\n🧑 You: ").strip()
            
            if not user_input:
                continue
            
            # Handle commands
            cmd = user_input.lower()
            
            if cmd in ['quit', 'exit']:
                print("\n👋 Goodbye!")
                break
            
            elif cmd == 'clear':
                assistant.clear_memory()
                print(" Conversation cleared")
                continue
            
            elif cmd == 'stats':
                stats = assistant.get_stats()
                print(f"\n📊 Statistics:")
                print(f"   Provider: {stats['llm_provider']}")
                print(f"   KB Documents: {stats['vector_store'].get('document_count', 0)}")
                print(f"   Memory Messages: {stats['memory_messages']}")
                continue
            
            elif cmd == 'help':
                print_help()
                continue
            
            elif cmd == 'rebuild':
                print(" Rebuilding knowledge base...")
                assistant.initialize(force_rebuild=True)
                continue
            
            elif cmd.startswith('add '):
                filepath = user_input[4:].strip()
                if os.path.exists(filepath):
                    assistant.add_document(filepath)
                else:
                    print(f" File not found: {filepath}")
                continue
            
            elif cmd.startswith('search '):
                query = user_input[7:].strip()
                results = assistant.search_knowledge_base(query)
                print(f"\n📑 Found {len(results)} results:\n")
                for i, r in enumerate(results, 1):
                    print(f"[{i}] {r['source']} (Page {r['page']})")
                    print(f"    {r['content'][:150]}...\n")
                continue
            
            elif cmd.startswith('kb '):
                question = user_input[3:].strip()
                response = assistant.force_rag(question)
                print(f"\n🤖 [KB Only]: {response['answer']}")
                continue
            
            elif cmd.startswith('general '):
                question = user_input[8:].strip()
                response = assistant.force_general(question)
                print(f"\n🤖 [General]: {response['answer']}")
                continue
            
            # Regular question - hybrid mode
            response = assistant.ask(user_input)
            
            # Show answer
            source_icon = "" if response['source_type'] == 'knowledge_base' else ""
            print(f"\n{source_icon} Assistant [{response['source_type']}]:")
            print(f"   {response['answer']}")
            
            # Show sources if from KB
            if response['sources']:
                print(f"\n📎 Sources:")
                for i, src in enumerate(response['sources'][:3], 1):
                    relevance = f" ({src['relevance']:.0%})" if src.get('relevance') else ""
                    print(f"   {i}. {src['source']} - Page {src['page']}{relevance}")
        
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n Error: {e}")
            logger.exception("Error in main loop")


if __name__ == "__main__":
    run_cli()