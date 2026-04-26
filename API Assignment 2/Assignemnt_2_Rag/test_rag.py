"""
Test and Demo script for RAG System
Run this to test the RAG system without the Streamlit UI
"""

import os
from dotenv import load_dotenv
from rag import RAGSystem
import json

# Load environment variables
load_dotenv()


def demo_rag_system():
    """Demonstrate RAG system functionality"""

    print("=" * 70)
    print("RAG System Demo")
    print("=" * 70)

    # Get API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY not found in environment variables")
        print("Please set it in .env file or environment")
        return

    # Initialize RAG System
    print("\n1️⃣ Initializing RAG System...")
    rag = RAGSystem(api_key=api_key)
    print("✓ RAG System initialized")

    # Create a sample PDF file for testing
    # (In real usage, user would upload actual PDF)
    sample_pdf_path = "./sample_document.pdf"

    # Check if sample PDF exists
    if not os.path.exists(sample_pdf_path):
        print(f"\n⚠️ Sample PDF not found at {sample_pdf_path}")
        print("To test the system:")
        print(f"  1. Place a PDF file at {sample_pdf_path}")
        print("  2. Run this script again")
        print("\nOr modify 'sample_pdf_path' to point to your PDF file")
        return

    # Process PDF
    print(f"\n2️⃣ Processing PDF: {sample_pdf_path}")
    success = rag.process_pdf(sample_pdf_path)

    if not success:
        print("✗ Failed to process PDF")
        return

    print("✓ PDF processed successfully")

    # Get collection stats
    print("\n3️⃣ Collection Statistics:")
    stats = rag.get_collection_stats()
    print(f"  - Collection Name: {stats.get('collection_name', 'N/A')}")
    print(f"  - Total Documents: {stats.get('total_documents', 0)}")
    print(f"  - Documents Metadata: {stats.get('documents_processed', {})}")

    # Perform searches with different K values
    queries = [
        ("What is the main topic?", 5),
        ("Summarize the key points", 3),
        ("What are the recommendations?", 5),
    ]

    print("\n4️⃣ Testing Retrieval with Different K Values:")
    print("-" * 70)

    for query, k in queries:
        print(f"\n📝 Query: {query}")
        print(f"   K Factor: {k}")

        # Retrieve documents
        retrieved = rag.retrieve(query, k=k)

        if retrieved:
            print(f"   ✓ Found {len(retrieved)} results")

            # Show top result
            top_result = retrieved[0]
            print(
                f"\n   Top Result (Similarity: {top_result['similarity_score']:.2%}):"
            )
            content = top_result["content"]
            if len(content) > 300:
                print(f"   {content[:300]}...")
            else:
                print(f"   {content}")

            print(f"\n   Metadata:")
            for key, value in top_result["metadata"].items():
                print(f"     - {key}: {value}")
        else:
            print("   ✗ No results found")

    # Generate answer
    print("\n5️⃣ Testing Answer Generation:")
    print("-" * 70)

    test_query = "What is the main topic?"
    print(f"\n📝 Query: {test_query}")

    retrieved = rag.retrieve(test_query, k=5)
    if retrieved:
        print("🤖 Generating answer...")
        answer = rag.generate_answer(test_query, retrieved)
        print(f"\n💡 Generated Answer:\n{answer}")
    else:
        print("✗ No documents to generate answer from")

    print("\n" + "=" * 70)
    print("✓ Demo completed successfully!")
    print("=" * 70)


def manual_test():
    """Manual test mode - interact with RAG system"""

    print("=" * 70)
    print("RAG System - Manual Test Mode")
    print("=" * 70)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY not found")
        return

    rag = RAGSystem(api_key=api_key)

    # PDF path input
    pdf_path = input("\nEnter PDF file path: ").strip()
    if not os.path.exists(pdf_path):
        print(f"ERROR: File not found: {pdf_path}")
        return

    # Process PDF
    print("\nProcessing PDF...")
    if not rag.process_pdf(pdf_path):
        print("Failed to process PDF")
        return

    # Interactive search loop
    print("\n" + "=" * 70)
    print("Ready for queries. Type 'exit' to quit.")
    print("=" * 70)

    while True:
        query = input("\n🔍 Enter your query: ").strip()

        if query.lower() == "exit":
            break

        if not query:
            print("Please enter a query")
            continue

        # Get K factor
        try:
            k = int(input("K Factor (default 5): ") or "5")
            k = max(1, min(20, k))  # Clamp between 1 and 20
        except ValueError:
            k = 5

        print(f"\nSearching with K={k}...")

        # Retrieve
        retrieved = rag.retrieve(query, k=k)

        if retrieved:
            print(f"\n✓ Found {len(retrieved)} results:\n")

            # Show results
            for doc in retrieved:
                print(
                    f"Result {doc['rank']} (Similarity: {doc['similarity_score']:.2%})"
                )
                print(f"  {doc['content'][:200]}...")
                print()

            # Generate answer
            gen_answer = input("Generate answer? (y/n): ").lower().strip()
            if gen_answer == "y":
                print("\n🤖 Generating answer...")
                answer = rag.generate_answer(query, retrieved)
                print(f"\n{answer}\n")
        else:
            print("✗ No relevant documents found")


if __name__ == "__main__":
    import sys

    print("\nRAG System Test Options:")
    print("1. Run demo (automatic test with sample)")
    print("2. Manual mode (interactive)")
    print("3. Exit")

    choice = input("\nSelect option (1-3): ").strip()

    if choice == "1":
        demo_rag_system()
    elif choice == "2":
        manual_test()
    else:
        print("Exiting...")
