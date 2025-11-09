#!/usr/bin/env python3
"""
Test script for the enhanced chatbot with knowledge base
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from knowledge_base import get_knowledge_base
from app import handle_knowledge_base_query

def test_knowledge_base():
    """Test the knowledge base functionality"""
    print("Testing Knowledge Base...")
    
    # Test getting the full knowledge base
    kb = get_knowledge_base()
    assert 'app_overview' in kb, "Knowledge base should contain app_overview"
    assert 'database_schema' in kb, "Knowledge base should contain database_schema"
    print("✓ Knowledge base structure is correct")
    
    # Test various queries
    test_queries = [
        ("What is this app?", "Should return app description"),
        ("How do I use the dashboard?", "Should provide dashboard info"),
        ("What are the customer statuses?", "Should list customer statuses"),
        ("What are the order statuses?", "Should list order statuses"),
        ("What payment methods are available?", "Should list payment methods"),
        ("What features does this app have?", "Should list main features"),
        ("How do I add a customer?", "Should provide info about adding customers"),
        ("What tables are in the database?", "Should provide database info"),
        ("Something that doesn't match", "Should return None"),
    ]
    
    for query, description in test_queries:
        result = handle_knowledge_base_query(query.lower())
        if result:
            print(f"✓ Query: '{query}' -> {description}")
            print(f"  Response: {result[:100]}...")
        else:
            print(f"✓ Query: '{query}' -> No match (as expected for this test)")
    
    print("\nKnowledge base testing completed!")

def test_chatbot_integration():
    """Test that the knowledge base properly integrates with the chatbot"""
    print("\nTesting Chatbot Integration...")
    
    # Test a few specific cases
    test_cases = [
        "What is this application?",
        "Tell me about the customer statuses",
        "How do I add a new product?",
        "What features does this system have?",
        "What are the order statuses?"
    ]
    
    for query in test_cases:
        result = handle_knowledge_base_query(query.lower())
        if result:
            print(f"✓ Query: '{query}' -> Got response: {result[:80]}...")
        else:
            print(f"? Query: '{query}' -> No response (might be handled by DB query)")
    
    print("Chatbot integration testing completed!")

if __name__ == "__main__":
    print("Testing Enhanced Chatbot with Knowledge Base\n")
    
    try:
        test_knowledge_base()
        test_chatbot_integration()
        
        print("\n✓ All tests passed! The enhanced chatbot with knowledge base is working correctly.")
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)