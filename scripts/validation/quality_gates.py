#!/usr/bin/env python3
"""
Quality Validation Automation - 5-Layer Framework
Implements automated quality gates for source validation

Usage:
    python3 scripts/validation/quality_gates.py validate --source-id <UUID>
    python3 scripts/validation/quality_gates.py check-recency --dimension theory
    python3 scripts/validation/quality_gates.py detect-contradictions
    python3 scripts/validation/quality_gates.py report
"""

import os
import sys
import argparse
import psycopg2
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

class QualityValidator:
    """5-Layer Quality Validation Framework"""
    
    def __init__(self, connection_string):
        self.conn = psycopg2.connect(connection_string)
        self.conn.autocommit = False
    
    def __del__(self):
        if self.conn:
            self.conn.close()
    
    # ========================================================================
    # LAYER 1: AUTHORITY SCORING (Pre-Ingestion)
    # ========================================================================
    
    def validate_authority_score(self, source_id: str, threshold: int = 70) -> Dict:
        """
        Validate authority score meets minimum threshold
        
        Args:
            source_id: UUID of source to validate
            threshold: Minimum authority score (default: 70)
        
        Returns:
            {'passed': bool, 'score': int, 'reason': str}
        """
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT authority_score, source_type, name
            FROM sources
            WHERE id = %s
        """, (source_id,))
        
        result = cursor.fetchone()
        cursor.close()
        
        if not result:
            return {
                'passed': False,
                'score': None,
                'reason': f'Source {source_id} not found'
            }
        
        score, source_type, name = result
        
        passed = score >= threshold
        
        validation = {
            'passed': passed,
            'score': score,
            'source_type': source_type,
            'name': name,
            'threshold': threshold,
            'reason': f"Authority score {score} {'meets' if passed else 'below'} threshold {threshold}"
        }
        
        # Log validation
        self._log_validation(source_id, 'authority', 'pass' if passed else 'fail', validation)
        
        return validation
    
    def block_low_authority_sources(self, threshold: int = 70) -> List[str]:
        """
        Find and block sources below authority threshold
        
        Returns:
            List of blocked source IDs
        """
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT id, name, authority_score, source_type
            FROM sources
            WHERE authority_score < %s
              AND validation_status != 'deprecated'
        """, (threshold,))
        
        low_authority = cursor.fetchall()
        blocked = []
        
        for source_id, name, score, source_type in low_authority:
            # Mark as flagged
            cursor.execute("""
                UPDATE sources
                SET validation_status = 'flagged',
                    deprecation_reason = %s
                WHERE id = %s
            """, (f"Authority score {score} below threshold {threshold}", source_id))
            
            blocked.append(source_id)
            
            print(f"⚠️  Blocked: {name} (score: {score}, type: {source_type})")
        
        self.conn.commit()
        cursor.close()
        
        return blocked
    
    # ========================================================================
    # LAYER 2: CROSS-SOURCE VERIFICATION
    # ========================================================================
    
    def verify_cross_references(self, source_id: str, min_supporting: int = 3) -> Dict:
        """
        Verify source has sufficient supporting sources
        
        Args:
            source_id: UUID of source to verify
            min_supporting: Minimum number of supporting sources (default: 3)
        
        Returns:
            {'confidence': str, 'supporting_count': int, 'passed': bool}
        """
        cursor = self.conn.cursor()
        
        # Count sources that cite or validate this source
        cursor.execute("""
            SELECT COUNT(DISTINCT source_id)
            FROM source_relationships
            WHERE related_source_id = %s
              AND relationship_type IN ('cites', 'validates', 'supports')
        """, (source_id,))
        
        supporting_count = cursor.fetchone()[0]
        cursor.close()
        
        if supporting_count >= min_supporting:
            confidence = 'high'
            passed = True
        elif supporting_count >= 2:
            confidence = 'moderate'
            passed = True
        elif supporting_count >= 1:
            confidence = 'low'
            passed = False
        else:
            confidence = 'single_source'
            passed = False
        
        validation = {
            'confidence': confidence,
            'supporting_count': supporting_count,
            'min_required': min_supporting,
            'passed': passed,
            'reason': f"{supporting_count} supporting sources ({'≥' if passed else '<'} {min_supporting})"
        }
        
        # Log validation
        self._log_validation(
            source_id,
            'cross_reference',
            'pass' if passed else 'warning',
            validation
        )
        
        return validation
    
    # ========================================================================
    # LAYER 3: RECENCY VALIDATION (Dimension-Specific)
    # ========================================================================
    
    def validate_recency(self, source_id: str) -> Dict:
        """
        Validate source freshness based on epistemological dimension
        
        Thresholds:
        - Theory: 10 years (foundational knowledge stable)
        - Practice: 2 years (tools/methods evolve)
        - Current: 1 year (must be recent)
        - Future: 2 years (forward-looking research)
        - History: No threshold (historical by nature)
        
        Returns:
            {'passed': bool, 'age_years': float, 'dimension': str, 'threshold_years': int}
        """
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT epistemological_dimension, publication_year, name
            FROM sources
            WHERE id = %s
        """, (source_id,))
        
        result = cursor.fetchone()
        cursor.close()
        
        if not result:
            return {'passed': False, 'reason': 'Source not found'}
        
        dimension, pub_year, name = result
        
        if not dimension or not pub_year:
            return {
                'passed': False,
                'reason': 'Missing epistemological dimension or publication year'
            }
        
        # Calculate age
        current_year = datetime.now().year
        age_years = current_year - pub_year
        
        # Dimension-specific thresholds
        thresholds = {
            'theory': 10,
            'practice': 2,
            'current': 1,
            'future': 2,
            'history': None  # No threshold (historical content)
        }
        
        threshold = thresholds.get(dimension)
        
        if threshold is None:
            # Historical sources have no recency requirement
            passed = True
            reason = 'Historical content (no recency requirement)'
        else:
            passed = age_years <= threshold
            reason = f"Age {age_years} years {'≤' if passed else '>'} threshold {threshold} years"
        
        validation = {
            'passed': passed,
            'age_years': age_years,
            'publication_year': pub_year,
            'dimension': dimension,
            'threshold_years': threshold,
            'reason': reason
        }
        
        # Log validation
        self._log_validation(
            source_id,
            'recency',
            'pass' if passed else 'warning',
            validation
        )
        
        return validation
    
    def check_outdated_sources(self) -> List[Dict]:
        """
        Find all sources that fail recency validation
        
        Returns:
            List of outdated sources with details
        """
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT id, name, epistemological_dimension, publication_year
            FROM sources
            WHERE epistemological_dimension IS NOT NULL
              AND publication_year IS NOT NULL
              AND validation_status != 'deprecated'
        """)
        
        sources = cursor.fetchall()
        cursor.close()
        
        outdated = []
        
        for source_id, name, dimension, pub_year in sources:
            validation = self.validate_recency(source_id)
            
            if not validation['passed']:
                outdated.append({
                    'id': source_id,
                    'name': name,
                    'dimension': dimension,
                    'age_years': validation['age_years'],
                    'threshold_years': validation['threshold_years']
                })
        
        return outdated
    
    # ========================================================================
    # LAYER 4: CUSTOMER FEEDBACK MONITORING
    # ========================================================================
    
    def check_customer_feedback(self, source_id: str, flag_threshold: int = 3) -> Dict:
        """
        Check customer feedback for accuracy issues
        
        Args:
            source_id: UUID of source to check
            flag_threshold: Number of flags to trigger manual review (default: 3)
        
        Returns:
            {'requires_review': bool, 'flag_count': int, 'avg_rating': float}
        """
        cursor = self.conn.cursor()
        
        # Count negative feedback
        cursor.execute("""
            SELECT 
                COUNT(*) as flag_count,
                AVG(rating) as avg_rating
            FROM source_feedback
            WHERE source_id = %s
              AND feedback_type IN ('accuracy_issue', 'outdated')
              AND resolved = false
        """, (source_id,))
        
        result = cursor.fetchone()
        flag_count, avg_rating = result
        
        # Get recent feedback
        cursor.execute("""
            SELECT feedback_type, rating, feedback_text, created_at
            FROM source_feedback
            WHERE source_id = %s
              AND resolved = false
            ORDER BY created_at DESC
            LIMIT 5
        """, (source_id,))
        
        recent_feedback = cursor.fetchall()
        cursor.close()
        
        requires_review = flag_count >= flag_threshold
        
        validation = {
            'requires_review': requires_review,
            'flag_count': flag_count,
            'flag_threshold': flag_threshold,
            'avg_rating': float(avg_rating) if avg_rating else None,
            'recent_feedback': [
                {
                    'type': fb[0],
                    'rating': fb[1],
                    'text': fb[2],
                    'date': fb[3].isoformat()
                }
                for fb in recent_feedback
            ]
        }
        
        # Log validation
        self._log_validation(
            source_id,
            'customer_feedback',
            'warning' if requires_review else 'pass',
            validation
        )
        
        return validation
    
    def flag_sources_for_review(self, flag_threshold: int = 3) -> List[str]:
        """
        Find sources with excessive negative feedback
        
        Returns:
            List of source IDs requiring manual review
        """
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT source_id, COUNT(*) as flag_count
            FROM source_feedback
            WHERE feedback_type IN ('accuracy_issue', 'outdated')
              AND resolved = false
              AND rating < 3
            GROUP BY source_id
            HAVING COUNT(*) >= %s
        """, (flag_threshold,))
        
        flagged = cursor.fetchall()
        
        flagged_ids = []
        for source_id, count in flagged:
            # Update validation status
            cursor.execute("""
                UPDATE sources
                SET validation_status = 'flagged'
                WHERE id = %s
            """, (source_id,))
            
            flagged_ids.append(source_id)
            
            print(f"⚠️  Flagged for review: {source_id} ({count} negative feedback)")
        
        self.conn.commit()
        cursor.close()
        
        return flagged_ids
    
    # ========================================================================
    # LAYER 5: CONTRADICTION DETECTION (LLM-Based)
    # ========================================================================
    
    def detect_contradictions(self, source_id: str) -> Dict:
        """
        Detect contradictions between sources (LLM-based)
        
        Note: This is a placeholder for future LLM integration.
        Currently returns not_implemented.
        
        Future implementation:
        1. Get source content
        2. Find related sources
        3. Use LLM to compare claims
        4. Flag contradictions for human review
        
        Returns:
            {'implemented': bool, 'reason': str}
        """
        # TODO: Implement LLM-based contradiction detection
        # Requires:
        # - OpenAI/Anthropic API integration
        # - Source content extraction
        # - Claim comparison logic
        # - Confidence scoring
        
        return {
            'implemented': False,
            'reason': 'LLM-based contradiction detection not yet implemented',
            'planned_features': [
                'Extract claims from source content',
                'Compare with related sources',
                'Use LLM to identify contradictions',
                'Flag for human review',
                'Track contradiction history'
            ]
        }
    
    # ========================================================================
    # QUALITY GATES WORKFLOW
    # ========================================================================
    
    def validate_source_complete(self, source_id: str) -> Dict:
        """
        Run complete validation suite on a source
        
        Returns:
            {
                'passed': bool,
                'layers': {
                    'authority': {...},
                    'cross_reference': {...},
                    'recency': {...},
                    'customer_feedback': {...},
                    'contradictions': {...}
                },
                'overall_status': str
            }
        """
        print(f"\n🔍 Running complete validation for source: {source_id}")
        
        results = {
            'source_id': source_id,
            'timestamp': datetime.now().isoformat(),
            'layers': {}
        }
        
        # Layer 1: Authority
        print("  Layer 1: Authority scoring...")
        results['layers']['authority'] = self.validate_authority_score(source_id)
        
        # Layer 2: Cross-reference
        print("  Layer 2: Cross-source verification...")
        results['layers']['cross_reference'] = self.verify_cross_references(source_id)
        
        # Layer 3: Recency
        print("  Layer 3: Recency validation...")
        results['layers']['recency'] = self.validate_recency(source_id)
        
        # Layer 4: Customer feedback
        print("  Layer 4: Customer feedback...")
        results['layers']['customer_feedback'] = self.check_customer_feedback(source_id)
        
        # Layer 5: Contradictions (not implemented yet)
        print("  Layer 5: Contradiction detection...")
        results['layers']['contradictions'] = self.detect_contradictions(source_id)
        
        # Determine overall status
        critical_failures = []
        warnings = []
        
        if not results['layers']['authority']['passed']:
            critical_failures.append('authority')
        
        if not results['layers']['cross_reference']['passed']:
            warnings.append('cross_reference')
        
        if not results['layers']['recency']['passed']:
            warnings.append('recency')
        
        if results['layers']['customer_feedback']['requires_review']:
            warnings.append('customer_feedback')
        
        # Overall pass/fail
        if critical_failures:
            results['overall_status'] = 'FAILED'
            results['passed'] = False
        elif warnings:
            results['overall_status'] = 'PASSED_WITH_WARNINGS'
            results['passed'] = True
        else:
            results['overall_status'] = 'PASSED'
            results['passed'] = True
        
        results['critical_failures'] = critical_failures
        results['warnings'] = warnings
        
        print(f"\n  ✅ Validation complete: {results['overall_status']}")
        if critical_failures:
            print(f"  ❌ Critical failures: {', '.join(critical_failures)}")
        if warnings:
            print(f"  ⚠️  Warnings: {', '.join(warnings)}")
        
        return results
    
    # ========================================================================
    # QUALITY GATE ENFORCEMENT
    # ========================================================================
    
    def enforce_quality_gates(self, source_id: str, target_environment: str) -> bool:
        """
        Enforce quality gates for environment promotion
        
        Args:
            source_id: UUID of source to promote
            target_environment: 'staging' or 'production'
        
        Returns:
            True if source passes quality gates, False otherwise
        """
        gates = {
            'staging': {
                'authority_threshold': 70,
                'cross_reference_min': 2,
                'allow_warnings': True
            },
            'production': {
                'authority_threshold': 75,
                'cross_reference_min': 3,
                'allow_warnings': False
            }
        }
        
        if target_environment not in gates:
            raise ValueError(f"Invalid environment: {target_environment}")
        
        gate = gates[target_environment]
        
        print(f"\n🚪 Enforcing quality gate: {target_environment}")
        print(f"   Authority threshold: {gate['authority_threshold']}")
        print(f"   Min cross-references: {gate['cross_reference_min']}")
        print(f"   Allow warnings: {gate['allow_warnings']}")
        
        # Run validation
        validation = self.validate_source_complete(source_id)
        
        # Check gates
        passed = True
        
        # Authority gate
        if validation['layers']['authority']['score'] < gate['authority_threshold']:
            print(f"  ❌ Failed authority gate: {validation['layers']['authority']['score']} < {gate['authority_threshold']}")
            passed = False
        
        # Cross-reference gate
        if validation['layers']['cross_reference']['supporting_count'] < gate['cross_reference_min']:
            print(f"  ❌ Failed cross-reference gate: {validation['layers']['cross_reference']['supporting_count']} < {gate['cross_reference_min']}")
            passed = False
        
        # Warning gate
        if not gate['allow_warnings'] and validation['warnings']:
            print(f"  ❌ Warnings not allowed in {target_environment}: {validation['warnings']}")
            passed = False
        
        if passed:
            print(f"  ✅ Passed quality gate: {target_environment}")
        else:
            print(f"  ❌ Failed quality gate: {target_environment}")
        
        return passed
    
    # ========================================================================
    # REPORTING
    # ========================================================================
    
    def generate_quality_report(self) -> Dict:
        """
        Generate comprehensive quality report for all sources
        
        Returns:
            {
                'total_sources': int,
                'by_status': {...},
                'failed_authority': [...],
                'outdated': [...],
                'flagged_feedback': [...]
            }
        """
        cursor = self.conn.cursor()
        
        # Total sources
        cursor.execute("SELECT COUNT(*) FROM sources")
        total = cursor.fetchone()[0]
        
        # By validation status
        cursor.execute("""
            SELECT validation_status, COUNT(*)
            FROM sources
            GROUP BY validation_status
        """)
        by_status = dict(cursor.fetchall())
        
        cursor.close()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_sources': total,
            'by_status': by_status,
            'failed_authority': self.block_low_authority_sources(threshold=70),
            'outdated': self.check_outdated_sources(),
            'flagged_feedback': self.flag_sources_for_review(flag_threshold=3)
        }
        
        return report
    
    def _log_validation(self, source_id: str, validation_type: str, result: str, details: Dict):
        """Log validation to source_validations table"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT INTO source_validations
            (source_id, validation_type, validation_result, validation_details)
            VALUES (%s, %s, %s, %s)
        """, (source_id, validation_type, result, json.dumps(details)))
        
        self.conn.commit()
        cursor.close()


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(description='Quality Validation Automation')
    parser.add_argument('command', choices=[
        'validate', 'check-authority', 'check-recency', 'check-feedback',
        'enforce-gate', 'report'
    ], help='Validation command')
    parser.add_argument('--source-id', type=str, help='Source UUID to validate')
    parser.add_argument('--dimension', type=str, help='Epistemological dimension filter')
    parser.add_argument('--environment', type=str, choices=['staging', 'production'], 
                       help='Target environment for quality gate')
    parser.add_argument('--output', type=str, help='Save report to JSON file')
    
    args = parser.parse_args()
    
    # Get connection string
    conn_str = os.getenv('DATABASE_URL')
    
    if not conn_str:
        try:
            import subprocess
            password = subprocess.check_output([
                'az', 'keyvault', 'secret', 'show',
                '--vault-name', 'fredesa-kv-e997e3',
                '--name', 'postgres-password',
                '--query', 'value',
                '-o', 'tsv'
            ], text=True).strip()
            
            conn_str = f"postgresql://fredesaadmin:{password}@fredesa-db-dev.postgres.database.azure.com:5432/postgres?sslmode=require"
        except Exception as e:
            print(f"❌ Could not get database credentials: {e}")
            sys.exit(1)
    
    # Initialize validator
    validator = QualityValidator(conn_str)
    
    # Execute command
    if args.command == 'validate':
        if not args.source_id:
            print("❌ --source-id required for validate command")
            sys.exit(1)
        
        result = validator.validate_source_complete(args.source_id)
        print(json.dumps(result, indent=2))
    
    elif args.command == 'check-authority':
        if args.source_id:
            result = validator.validate_authority_score(args.source_id)
            print(json.dumps(result, indent=2))
        else:
            blocked = validator.block_low_authority_sources()
            print(f"\n✅ Blocked {len(blocked)} low-authority sources")
    
    elif args.command == 'check-recency':
        if args.source_id:
            result = validator.validate_recency(args.source_id)
            print(json.dumps(result, indent=2))
        else:
            outdated = validator.check_outdated_sources()
            print(f"\n📅 Found {len(outdated)} outdated sources:")
            for source in outdated[:10]:  # Show first 10
                print(f"  - {source['name']} ({source['dimension']}, {source['age_years']} years old)")
    
    elif args.command == 'check-feedback':
        if not args.source_id:
            flagged = validator.flag_sources_for_review()
            print(f"\n⚠️  Flagged {len(flagged)} sources for review")
        else:
            result = validator.check_customer_feedback(args.source_id)
            print(json.dumps(result, indent=2))
    
    elif args.command == 'enforce-gate':
        if not args.source_id or not args.environment:
            print("❌ --source-id and --environment required for enforce-gate command")
            sys.exit(1)
        
        passed = validator.enforce_quality_gates(args.source_id, args.environment)
        sys.exit(0 if passed else 1)
    
    elif args.command == 'report':
        report = validator.generate_quality_report()
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"📁 Report saved to: {args.output}")
        else:
            print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
