#!/usr/bin/env python3
"""
Knowledge Gap Manager - Environment-Aware Learning System

Development: Auto-ingest knowledge gaps (rapid learning)
Production: Log gaps + notify dev team (security-first)

Complies with:
- OWASP API5:2023 (Broken Function Level Authorization)
- NIST AC-3 (Access Enforcement)
- AWS SaaS Lens (Tenant Isolation)
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import requests
import yaml

REPO_ROOT = Path(__file__).parent.parent.parent
SOURCES_FILE = REPO_ROOT / "config" / "sources.yaml"
GAPS_LOG = REPO_ROOT / "logs" / "knowledge_gaps.jsonl"
GAPS_QUEUE = REPO_ROOT / "logs" / "production_gaps_queue.jsonl"


class EnvironmentConfig:
    """Environment-specific configuration"""
    
    def __init__(self):
        self.environment = os.getenv("ENVIRONMENT", "development").lower()
        self.is_production = self.environment in ["production", "prod", "staging"]
        self.enable_auto_ingest = os.getenv("ENABLE_AUTO_LEARNING", "true").lower() == "true"
        self.slack_webhook = os.getenv("SLACK_WEBHOOK_URL")  # For dev notifications
        self.dev_api_endpoint = os.getenv("DEV_KNOWLEDGE_API")  # Send gaps to dev
        
        # Production safety check
        if self.is_production and self.enable_auto_ingest:
            raise EnvironmentError(
                "⚠️  SECURITY VIOLATION: Autonomous learning cannot be enabled in production.\n"
                "Set ENABLE_AUTO_LEARNING=false or change ENVIRONMENT to 'development'.\n"
                "Reason: OWASP API5 (Broken Function Level Authorization) - customers "
                "could trigger ingestion to bypass tier restrictions."
            )
    
    def __repr__(self):
        return (
            f"EnvironmentConfig(environment={self.environment}, "
            f"production={self.is_production}, "
            f"auto_ingest={self.enable_auto_ingest})"
        )


class KnowledgeGapManager:
    """Manages knowledge gaps with environment awareness"""
    
    def __init__(self):
        self.config = EnvironmentConfig()
        self.sources = self._load_sources()
        
        # Ensure log directories exist
        GAPS_LOG.parent.mkdir(parents=True, exist_ok=True)
        GAPS_QUEUE.parent.mkdir(parents=True, exist_ok=True)
    
    def _load_sources(self) -> Dict:
        """Load current sources.yaml"""
        with open(SOURCES_FILE, "r") as f:
            return yaml.safe_load(f)
    
    def detect_gap(
        self, 
        topic: str, 
        keywords: List[str],
        customer_id: Optional[str] = None,
        query_context: Optional[str] = None
    ) -> Dict:
        """
        Detect knowledge gap and handle according to environment
        
        Args:
            topic: Topic area (e.g., "ITAR compliance")
            keywords: Search keywords that failed to match
            customer_id: Customer who triggered the gap (production only)
            query_context: User's original query
        
        Returns:
            Gap detection result with action taken
        """
        # Check existing coverage
        matching_sources = self._find_matching_sources(keywords)
        has_sufficient_coverage = len(matching_sources) >= 2
        
        gap_record = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "topic": topic,
            "keywords": keywords,
            "matching_sources": matching_sources,
            "coverage_sufficient": has_sufficient_coverage,
            "environment": self.config.environment,
            "customer_id": customer_id,
            "query_context": query_context
        }
        
        if has_sufficient_coverage:
            return {
                "gap_detected": False,
                "sources_found": len(matching_sources),
                "action": "none_needed"
            }
        
        # Gap detected - route based on environment
        if self.config.is_production:
            return self._handle_production_gap(gap_record)
        else:
            return self._handle_development_gap(gap_record)
    
    def _find_matching_sources(self, keywords: List[str]) -> List[str]:
        """Find sources matching keywords"""
        matching = []
        
        for source in self.sources.get("sources", []):
            source_id = source.get("id")
            name = source.get("name", "").lower()
            tags = [tag.lower() for tag in source.get("metadata_tags", [])]
            category = source.get("category", "").lower()
            
            # Calculate keyword match score
            keyword_matches = sum(
                1 for kw in keywords
                if kw.lower() in name or
                   kw.lower() in " ".join(tags) or
                   kw.lower() in category
            )
            
            if keyword_matches >= len(keywords) * 0.6:  # 60% match threshold
                matching.append(source_id)
        
        return matching
    
    def _handle_production_gap(self, gap_record: Dict) -> Dict:
        """
        Production gap handling: LOG + NOTIFY DEV (never auto-ingest)
        
        Complies with:
        - OWASP API5: No customer-triggered ingestion
        - NIST AC-3: Access control enforced
        - NIST AI RMF: Human-in-loop governance
        """
        # 1. Log to production gaps queue
        with open(GAPS_QUEUE, "a") as f:
            f.write(json.dumps(gap_record) + "\n")
        
        # 2. Notify development team
        notification_sent = self._notify_development_team(gap_record)
        
        # 3. Return customer-safe message
        return {
            "gap_detected": True,
            "action": "logged_for_review",
            "message": (
                "We've identified this knowledge area for enhancement. "
                "Our team will review and expand coverage in the next update."
            ),
            "notification_sent": notification_sent,
            "queue_position": self._count_queue_items()
        }
    
    def _handle_development_gap(self, gap_record: Dict) -> Dict:
        """
        Development gap handling: AUTO-INGEST (rapid learning enabled)
        
        Safe because:
        - Single-tenant environment
        - No customer data exposure risk
        - Controlled by developers
        """
        # Log the gap
        with open(GAPS_LOG, "a") as f:
            f.write(json.dumps(gap_record) + "\n")
        
        if not self.config.enable_auto_ingest:
            return {
                "gap_detected": True,
                "action": "logged_only",
                "message": "Auto-ingestion disabled. Gap logged for manual review."
            }
        
        # In development, can proceed with autonomous learning
        print(f"🔍 Knowledge gap detected: {gap_record['topic']}")
        print(f"📚 Keywords: {', '.join(gap_record['keywords'])}")
        print(f"💡 Development mode: Auto-ingestion available")
        print(f"ℹ️  To ingest, run: python3 scripts/automation/autonomous_learning_agent.py")
        
        return {
            "gap_detected": True,
            "action": "ready_for_ingestion",
            "message": "Gap logged. Run autonomous_learning_agent.py to ingest.",
            "suggested_keywords": gap_record["keywords"]
        }
    
    def _notify_development_team(self, gap_record: Dict) -> bool:
        """
        Notify development team about production knowledge gap
        
        Methods:
        1. Slack webhook (if configured)
        2. HTTP POST to dev API (if configured)
        3. Email alert (future)
        """
        notifications_sent = []
        
        # 1. Slack notification
        if self.config.slack_webhook:
            try:
                message = self._format_slack_message(gap_record)
                response = requests.post(
                    self.config.slack_webhook,
                    json={"text": message},
                    timeout=5
                )
                if response.status_code == 200:
                    notifications_sent.append("slack")
            except Exception as e:
                print(f"⚠️  Slack notification failed: {e}")
        
        # 2. Dev API notification
        if self.config.dev_api_endpoint:
            try:
                response = requests.post(
                    f"{self.config.dev_api_endpoint}/knowledge-gaps",
                    json=gap_record,
                    headers={"Content-Type": "application/json"},
                    timeout=5
                )
                if response.status_code in [200, 201]:
                    notifications_sent.append("dev_api")
            except Exception as e:
                print(f"⚠️  Dev API notification failed: {e}")
        
        # 3. File-based notification (always works)
        try:
            notification_file = REPO_ROOT / "logs" / "dev_notifications.jsonl"
            with open(notification_file, "a") as f:
                f.write(json.dumps({
                    **gap_record,
                    "notification_timestamp": datetime.utcnow().isoformat() + "Z"
                }) + "\n")
            notifications_sent.append("file")
        except Exception as e:
            print(f"⚠️  File notification failed: {e}")
        
        return len(notifications_sent) > 0
    
    def _format_slack_message(self, gap_record: Dict) -> str:
        """Format production gap as Slack message"""
        customer = gap_record.get("customer_id", "unknown")
        topic = gap_record.get("topic")
        keywords = ", ".join(gap_record.get("keywords", []))
        context = gap_record.get("query_context", "N/A")
        
        return (
            f"🔍 *Knowledge Gap Detected in Production*\n\n"
            f"*Customer:* {customer}\n"
            f"*Topic:* {topic}\n"
            f"*Keywords:* {keywords}\n"
            f"*Query:* {context}\n\n"
            f"*Action Required:* Review and consider ingesting sources for this topic.\n"
            f"*Queue Position:* {self._count_queue_items()}\n"
            f"*View Queue:* `cat logs/production_gaps_queue.jsonl`"
        )
    
    def _count_queue_items(self) -> int:
        """Count items in production gaps queue"""
        try:
            with open(GAPS_QUEUE, "r") as f:
                return sum(1 for _ in f)
        except FileNotFoundError:
            return 0
    
    def get_production_gaps(self, limit: int = 50) -> List[Dict]:
        """Retrieve production gaps for dev team review"""
        try:
            with open(GAPS_QUEUE, "r") as f:
                gaps = [json.loads(line) for line in f]
            return gaps[-limit:]  # Most recent N gaps
        except FileNotFoundError:
            return []
    
    def mark_gap_resolved(self, gap_timestamp: str):
        """
        Mark a gap as resolved (source ingested in dev)
        Removes from queue
        """
        try:
            with open(GAPS_QUEUE, "r") as f:
                gaps = [json.loads(line) for line in f]
            
            # Filter out resolved gap
            remaining = [g for g in gaps if g.get("timestamp") != gap_timestamp]
            
            # Rewrite queue
            with open(GAPS_QUEUE, "w") as f:
                for gap in remaining:
                    f.write(json.dumps(gap) + "\n")
            
            return True
        except Exception as e:
            print(f"❌ Failed to mark gap resolved: {e}")
            return False


# CLI for development team
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Knowledge Gap Manager - Environment-aware learning"
    )
    parser.add_argument(
        "--view-queue",
        action="store_true",
        help="View production gaps queue"
    )
    parser.add_argument(
        "--test-gap",
        metavar="TOPIC",
        help="Test gap detection (dev only)"
    )
    parser.add_argument(
        "--resolve",
        metavar="TIMESTAMP",
        help="Mark gap as resolved"
    )
    parser.add_argument(
        "--config",
        action="store_true",
        help="Show current environment configuration"
    )
    
    args = parser.parse_args()
    
    manager = KnowledgeGapManager()
    
    if args.config:
        print("🔧 Current Configuration:")
        print(f"   {manager.config}")
        print(f"\n📊 Production Gaps in Queue: {manager._count_queue_items()}")
    
    elif args.view_queue:
        gaps = manager.get_production_gaps()
        print(f"📋 Production Knowledge Gaps ({len(gaps)} total)\n")
        for i, gap in enumerate(gaps, 1):
            print(f"{i}. {gap['topic']}")
            print(f"   Keywords: {', '.join(gap['keywords'])}")
            print(f"   Customer: {gap.get('customer_id', 'N/A')}")
            print(f"   Time: {gap['timestamp']}")
            print()
    
    elif args.test_gap:
        result = manager.detect_gap(
            topic=args.test_gap,
            keywords=args.test_gap.split(),
            query_context=f"Test query about {args.test_gap}"
        )
        print(f"✅ Gap Detection Result:")
        print(json.dumps(result, indent=2))
    
    elif args.resolve:
        if manager.mark_gap_resolved(args.resolve):
            print(f"✅ Gap marked as resolved: {args.resolve}")
        else:
            print(f"❌ Failed to resolve gap")
    
    else:
        parser.print_help()
