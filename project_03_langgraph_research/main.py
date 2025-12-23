"""Main entry point for the LangGraph Research Assistant"""

import os
from pathlib import Path
from dotenv import load_dotenv
from graph.state import create_initial_state
from graph.workflow import create_research_workflow, visualize_workflow

# Load .env from parent directory (root of Agentic_ai)
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)


def print_banner():
    """Print startup banner"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        🔬 LANGGRAPH RESEARCH ASSISTANT                        ║
║                                                              ║
║        Multi-Agent AI Research with State Graphs             ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""")


def print_results(state):
    """Pretty print the final results"""
    print("\n" + "="*60)
    print("📋 RESEARCH RESULTS")
    print("="*60)
    print(f"\n📌 Topic: {state['topic']}")
    print(f"🔍 Search Attempts: {state['search_attempts']}")
    print(f"⭐ Quality Score: {state.get('quality_score', 0)}/10")
    
    print(f"\n{'='*60}")
    print("📄 SUMMARY")
    print("="*60)
    print(state.get('summary', 'No summary available'))
    
    if state.get('key_points'):
        print(f"\n{'='*60}")
        print("🔑 KEY POINTS")
        print("="*60)
        for i, point in enumerate(state['key_points'], 1):
            print(f"{i}. {point}")
    
    print("\n" + "="*60 + "\n")


def main():
    """Main function"""
    
    # Print banner
    print_banner()
    
    # Show workflow structure
    visualize_workflow()
    
    # Check environment
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ Error: GOOGLE_API_KEY not found in .env file")
        print("   Please copy .env.example to .env and add your API key")
        return
    
    if not os.getenv("TAVILY_API_KEY"):
        print("❌ Error: TAVILY_API_KEY not found in .env file")
        print("   Please copy .env.example to .env and add your API key")
        return
    
    # Get user input
    print("🎯 What would you like to research?")
    print("   Examples:")
    print("   - 'Latest developments in quantum computing'")
    print("   - 'Impact of AI on healthcare'")
    print("   - 'Trends in sustainable energy'")
    print()
    
    topic = input("📝 Enter research topic: ").strip()
    
    if not topic:
        print("❌ No topic entered. Exiting.")
        return
    
    print(f"\n🚀 Starting research on: '{topic}'")
    print("   This may take 30-60 seconds...\n")
    
    try:
        # Create workflow
        app = create_research_workflow()
        
        # Create initial state
        initial_state = create_initial_state(topic)
        
        # Run the workflow!
        print("="*60)
        print("🤖 EXECUTING LANGGRAPH WORKFLOW")
        print("="*60)
        
        # Invoke the graph
        final_state = app.invoke(initial_state)
        
        # Print results
        print_results(final_state)
        
        # Success!
        print("✅ Research complete!")
        
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
