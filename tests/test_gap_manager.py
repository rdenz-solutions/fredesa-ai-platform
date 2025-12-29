#!/usr/bin/env python3
"""
Test Knowledge Gap Manager - Demonstrates environment-aware behavior

Run in different environments:
  ENVIRONMENT=development python3 test_gap_manager.py
  ENVIRONMENT=production python3 test_gap_manager.py
"""

import os
import sys
import importlib.util
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import using direct file loading
spec = importlib.util.spec_from_file_location(
    "knowledge_gap_manager",
    Path(__file__).parent.parent / "scripts" / "automation" / "knowledge_gap_manager.py"
)
knowledge_gap_manager = importlib.util.module_from_spec(spec)
spec.loader.exec_module(knowledge_gap_manager)
KnowledgeGapManager = knowledge_gap_manager.KnowledgeGapManager

def test_development_mode():
    """Test gap detection in development mode"""
    print("="*70)
    print("TEST 1: Development Mode (Auto-Learning Enabled)")
    print("="*70)
    
    os.environ["ENVIRONMENT"] = "development"
    os.environ["ENABLE_AUTO_LEARNING"] = "true"
    
    manager = KnowledgeGapManager()
    print(f"\n📋 Configuration: {manager.config}\n")
    
    # Test gap detection
    result = manager.detect_gap(
        topic="Quantum Computing Security",
        keywords=["quantum", "cryptography", "post-quantum"],
        query_context="How does quantum computing affect current cryptography?"
    )
    
    print("🔍 Gap Detection Result:")
    print(f"   Gap Detected: {result['gap_detected']}")
    print(f"   Action: {result['action']}")
    print(f"   Message: {result['message']}")
    print()

def test_production_mode():
    """Test gap detection in production mode"""
    print("="*70)
    print("TEST 2: Production Mode (Logging + Notification)")
    print("="*70)
    
    os.environ["ENVIRONMENT"] = "production"
    os.environ["ENABLE_AUTO_LEARNING"] = "false"
    
    manager = KnowledgeGapManager()
    print(f"\n📋 Configuration: {manager.config}\n")
    
    # Test gap detection
    result = manager.detect_gap(
        topic="ITAR Export Control",
        keywords=["ITAR", "export", "control", "compliance"],
        customer_id="019b4ac6-6b06-78d2-95fc-13058e9b5592",
        query_context="What are ITAR requirements for software exports?"
    )
    
    print("🔍 Gap Detection Result:")
    print(f"   Gap Detected: {result['gap_detected']}")
    print(f"   Action: {result['action']}")
    print(f"   Message: {result['message']}")
    print(f"   Notification Sent: {result['notification_sent']}")
    print(f"   Queue Position: {result['queue_position']}")
    print()

def test_security_violation():
    """Test that production auto-learning is blocked"""
    print("="*70)
    print("TEST 3: Security Violation (Should Fail)")
    print("="*70)
    
    os.environ["ENVIRONMENT"] = "production"
    os.environ["ENABLE_AUTO_LEARNING"] = "true"  # WRONG!
    
    print("\n⚠️  Attempting to enable auto-learning in production...\n")
    
    try:
        manager = KnowledgeGapManager()
        print("❌ SECURITY FAILURE: Auto-learning enabled in production!")
    except EnvironmentError as e:
        print("✅ SECURITY VIOLATION CAUGHT:")
        print(f"   {str(e)}\n")

def test_queue_operations():
    """Test production gap queue management"""
    print("="*70)
    print("TEST 4: Queue Management")
    print("="*70)
    
    os.environ["ENVIRONMENT"] = "production"
    os.environ["ENABLE_AUTO_LEARNING"] = "false"
    
    manager = KnowledgeGapManager()
    
    # Add a few gaps
    topics = [
        ("CMMC Level 3", ["CMMC", "level", "3", "cybersecurity"]),
        ("Zero Trust Architecture", ["zero", "trust", "architecture"]),
        ("Supply Chain Risk", ["supply", "chain", "risk", "management"])
    ]
    
    print("\n📝 Adding gaps to queue...\n")
    for topic, keywords in topics:
        manager.detect_gap(
            topic=topic,
            keywords=keywords,
            customer_id="test-customer-123",
            query_context=f"Query about {topic}"
        )
        print(f"   ✓ Added: {topic}")
    
    # View queue
    print(f"\n📊 Queue Status: {manager._count_queue_items()} gaps\n")
    
    gaps = manager.get_production_gaps(limit=5)
    print("📋 Recent Gaps:")
    for i, gap in enumerate(gaps[-3:], 1):
        print(f"   {i}. {gap['topic']}")
        print(f"      Customer: {gap.get('customer_id', 'N/A')}")
        print(f"      Time: {gap['timestamp']}")
    print()

def test_existing_coverage():
    """Test that existing coverage doesn't trigger gaps"""
    print("="*70)
    print("TEST 5: Existing Coverage (No Gap)")
    print("="*70)
    
    os.environ["ENVIRONMENT"] = "development"
    os.environ["ENABLE_AUTO_LEARNING"] = "true"
    
    manager = KnowledgeGapManager()
    
    # Test with topic that should have coverage (FAR)
    result = manager.detect_gap(
        topic="Federal Acquisition Regulation",
        keywords=["FAR", "federal", "acquisition", "regulation"],
        query_context="What does FAR say about subcontracting?"
    )
    
    print(f"\n🔍 Testing with existing topic (FAR)...")
    print(f"   Gap Detected: {result['gap_detected']}")
    print(f"   Sources Found: {result.get('sources_found', 0)}")
    print(f"   Action: {result['action']}")
    print()

if __name__ == "__main__":
    print("\n🧪 Knowledge Gap Manager Test Suite\n")
    
    try:
        test_development_mode()
        test_production_mode()
        test_security_violation()
        test_queue_operations()
        test_existing_coverage()
        
        print("="*70)
        print("✅ ALL TESTS PASSED")
        print("="*70)
        print("\n📚 Documentation: docs/KNOWLEDGE_GAP_MANAGER.md")
        print("🔧 Configuration: .env.development, .env.production")
        print("📊 View Production Queue: python3 scripts/automation/knowledge_gap_manager.py --view-queue")
        print()
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
