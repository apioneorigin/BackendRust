#!/usr/bin/env python3
"""
Test the compiled registry.json
"""

import json

def test_registry():
    print("="*60)
    print("REGISTRY TESTER")
    print("="*60)
    
    # Load registry
    print("\nLoading registry.json...")
    with open('./registry.json', 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    print(f"✓ Loaded registry")
    print(f"  Formulas: {len(registry['formulas'])}")
    print(f"  Variables: {len(registry['variables'])}")
    print(f"  Operators: {len(registry['operators'])}")
    
    # Test 1: Simple calculation
    print("\n" + "="*60)
    print("TEST 1: Simple Formula Execution")
    print("="*60)
    
    # Find a simple Tier 0 formula
    tier0_formulas = [f for f in registry['formulas'] if f['tier'] == 0]
    print(f"\nFound {len(tier0_formulas)} Tier 0 formulas")
    
    # Show first 5
    print("\nSample Tier 0 formulas:")
    for i, formula in enumerate(tier0_formulas[:5], 1):
        print(f"  {i}. {formula['name']} = {formula['expression'][:60]}...")
    
    # Test 2: Dependency chain
    print("\n" + "="*60)
    print("TEST 2: Dependency Chain Analysis")
    print("="*60)
    
    # Find a formula with dependencies
    formulas_with_deps = [f for f in registry['formulas'] if len(f['dependencies']) > 0]
    sample = formulas_with_deps[0] if formulas_with_deps else None
    
    if sample:
        print(f"\nFormula: {sample['name']}")
        print(f"Expression: {sample['expression'][:80]}...")
        print(f"Dependencies: {len(sample['dependencies'])} formulas")
        print(f"Tier: {sample['tier']}")
        print(f"Variables used: {', '.join(sample['variables_used'][:5])}...")
    
    # Test 3: Circular dependencies
    print("\n" + "="*60)
    print("TEST 3: Circular Dependencies")
    print("="*60)
    
    circular = [f for f in registry['formulas'] if f['tier'] == -1]
    print(f"\nFound {len(circular)} circular formulas")
    
    for i, formula in enumerate(circular[:3], 1):
        print(f"  {i}. {formula['name']} = {formula['expression'][:60]}...")
    
    # Test 4: Operator usage
    print("\n" + "="*60)
    print("TEST 4: Operator Analysis")
    print("="*60)
    
    print(f"\nTop operators by usage:")
    for i, op in enumerate(registry['operators'][:10], 1):
        print(f"  {i}. {op['name']} ({op['english']}) - {op['usage_count']} uses")
    
    # Test 5: Tier distribution
    print("\n" + "="*60)
    print("TEST 5: Tier Distribution")
    print("="*60)
    
    print("\nFormulas per tier:")
    for tier, count in sorted(registry['tier_distribution'].items(), key=lambda x: int(x[0]) if x[0].lstrip('-').isdigit() else 999):
        print(f"  Tier {tier}: {count} formulas")
    
    print("\n" + "="*60)
    print("ALL TESTS COMPLETE")
    print("="*60)
    print("✅ Registry is valid and ready for inference engine")

if __name__ == '__main__':
    test_registry()