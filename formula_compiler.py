#!/usr/bin/env python3
"""
Formula Compiler for One Origin Framework (OOF)
Converts OOF.txt into machine-readable registry.json
"""

import os
import json
import re
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Set, Any, Optional

# ============================================================================
# STEP 1: SETUP & FILE READING
# ============================================================================

class FormulaCompiler:
    def __init__(self, input_file: str, output_file: str):
        self.input_file = input_file
        self.output_file = output_file
        
        # Metadata tracker
        self.metadata = {
            'source_file': input_file,
            'total_lines': 0,
            'empty_lines': 0,
            'comment_lines': 0,
            'formula_lines': 0,
            'documentation_lines': 0,
            'code_block_lines': 0,
            'parsing_errors': [],
            'parsing_warnings': [],
            'start_time': datetime.now().isoformat(),
            'end_time': None
        }
        
        # Data structures (will populate in later steps)
        self.raw_lines = []
        self.lines = []
        self.formulas = []
        self.variables = {}
        self.operators = []
        self.dependencies = {}
        self.confidence_rules = {}
        
    def load_file(self):
        """Load OOF.txt and create line objects"""
        print(f"Loading {self.input_file}...")
        
        # Check if file exists
        if not os.path.exists(self.input_file):
            error = f"ERROR: File not found: {self.input_file}"
            self.metadata['parsing_errors'].append(error)
            print(error)
            return False
        
        # Read file
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                self.raw_lines = f.readlines()
        except UnicodeDecodeError:
            try:
                with open(self.input_file, 'r', encoding='latin-1') as f:
                    self.raw_lines = f.readlines()
                self.metadata['parsing_warnings'].append("Used latin-1 encoding fallback")
            except Exception as e:
                error = f"ERROR: Could not read file: {str(e)}"
                self.metadata['parsing_errors'].append(error)
                print(error)
                return False
        
        self.metadata['total_lines'] = len(self.raw_lines)
        print(f"✓ Loaded {self.metadata['total_lines']} lines")
        
        # Create line objects
        self._create_line_objects()
        
        # First-pass classification
        self._classify_lines()
        
        # Print summary
        self._print_load_summary()
        
        return True
    
    def _create_line_objects(self):
        """Transform raw lines into structured objects"""
        for i, raw_line in enumerate(self.raw_lines):
            text = raw_line.strip()
            
            line_obj = {
                'line_number': i + 1,
                'raw_text': raw_line,
                'text': text,
                'type': 'UNKNOWN',
                'is_empty': len(text) == 0,
                'length': len(text)
            }
            
            self.lines.append(line_obj)
    
    def _classify_lines(self):
        """First-pass classification of line types"""
        inside_code_block = False
        
        for line in self.lines:
            # Empty lines
            if line['is_empty']:
                line['type'] = 'EMPTY'
                self.metadata['empty_lines'] += 1
                continue
            
            text = line['text']
            
            # Code block delimiters
            if text.startswith('```'):
                inside_code_block = not inside_code_block
                line['type'] = 'CODE_BLOCK_DELIMITER'
                self.metadata['code_block_lines'] += 1
                continue
            
            # Inside code block
            if inside_code_block:
                line['type'] = 'CODE_BLOCK'
                self.metadata['code_block_lines'] += 1
                continue
            
            # Comments
            if text.startswith('#') or text.startswith('//'):
                line['type'] = 'COMMENT'
                self.metadata['comment_lines'] += 1
                continue
            
            # Formulas (contains = sign, not in URL)
            if '=' in text and not text.startswith('http'):
                # Quick check: make sure it's not part of markdown or other syntax
                if not text.startswith('-') and not text.startswith('*'):
                    line['type'] = 'FORMULA'
                    self.metadata['formula_lines'] += 1
                    continue
            
            # Everything else is documentation
            line['type'] = 'DOCUMENTATION'
            self.metadata['documentation_lines'] += 1
    
    def _print_load_summary(self):
        """Print loading statistics"""
        print("\n" + "="*60)
        print("FILE LOADING SUMMARY")
        print("="*60)
        print(f"Total lines:         {self.metadata['total_lines']}")
        print(f"Empty lines:         {self.metadata['empty_lines']}")
        print(f"Comment lines:       {self.metadata['comment_lines']}")
        print(f"Code block lines:    {self.metadata['code_block_lines']}")
        print(f"Formula lines:       {self.metadata['formula_lines']}")
        print(f"Documentation lines: {self.metadata['documentation_lines']}")
        print("="*60 + "\n")
        
        if self.metadata['parsing_warnings']:
            print("WARNINGS:")
            for warning in self.metadata['parsing_warnings']:
                print(f"  ⚠ {warning}")
            print()

# ============================================================================
    # STEP 2: PARSE INDIVIDUAL FORMULAS
    # ============================================================================
    
    def parse_formulas(self):
        """Extract and parse each formula into structured components"""
        print("\nParsing formulas...")
        
        # Get all formula lines
        formula_lines = [line for line in self.lines if line['type'] == 'FORMULA']
        
        formula_id = 1
        for line in formula_lines:
            try:
                formula_obj = self._parse_single_formula(line, formula_id)
                if formula_obj:
                    self.formulas.append(formula_obj)
                    formula_id += 1
            except Exception as e:
                error = f"Line {line['line_number']}: {str(e)}"
                self.metadata['parsing_errors'].append(error)
        
        print(f"✓ Parsed {len(self.formulas)} formulas")
        self._print_formula_summary()
    
    def _parse_single_formula(self, line: Dict, formula_id: int) -> Optional[Dict]:
        """Parse a single formula line into components"""
        text = line['text']
        
        # Split on equals sign
        if '=' not in text:
            return None
        
        parts = text.split('=', 1)
        if len(parts) != 2:
            return None
        
        left_side = parts[0].strip()
        right_side = parts[1].strip()
        
        # Skip if looks like markdown or not a real formula
        if not left_side or not right_side:
            return None
        
        # Extract output variable (clean up any annotations)
        output_variable = self._extract_output_variable(left_side)
        
        # Parse the expression
        variables_used = self._extract_variables(right_side)
        operators_used = self._extract_operators(right_side)
        
        # Extract consciousness level if present
        consciousness_level = self._extract_consciousness_level(text)
        
        # Create formula object
        formula_obj = {
            'id': formula_id,
            'name': output_variable,
            'expression': right_side,
            'variables_used': list(variables_used),
            'operators_used': list(operators_used),
            'consciousness_level': consciousness_level,
            'original_line_number': line['line_number'],
            'original_text': text,
            'dependencies': [],  # Will fill in Step 5
            'tier': None  # Will fill in Step 6
        }
        
        return formula_obj
    
    def _extract_output_variable(self, left_side: str) -> str:
        """Extract the variable name from left side of equation"""
        # Remove any consciousness level annotations like [S3]
        cleaned = re.sub(r'\[S\d+\]', '', left_side).strip()
        
        # Remove any parentheses
        cleaned = cleaned.replace('(', '').replace(')', '').strip()
        
        # Take first word if multiple
        if ' ' in cleaned:
            cleaned = cleaned.split()[0]
        
        return cleaned
    
    def _extract_variables(self, expression: str) -> Set[str]:
        """Extract all variable names from expression"""
        # Remove operators and parentheses
        temp = expression
        operators = ['+', '-', '*', '×', '/', '^', '→', '←', '↔', '⊕', '⊗', '∧', '∨', '¬', '=', '<', '>', '≤', '≥']
        for op in operators:
            temp = temp.replace(op, ' ')
        
        temp = temp.replace('(', ' ').replace(')', ' ')
        temp = temp.replace('[', ' ').replace(']', ' ')
        temp = temp.replace('{', ' ').replace('}', ' ')
        
        # Split and filter
        words = temp.split()
        variables = set()
        
        for word in words:
            word = word.strip()
            # Skip numbers
            if word.replace('.', '').replace('-', '').isdigit():
                continue
            # Skip empty
            if not word:
                continue
            # Skip single letters that might be constants
            if len(word) == 1 and word.lower() in ['e', 'i', 'π']:
                continue
            
            variables.add(word)
        
        return variables
    
    def _extract_operators(self, expression: str) -> Set[str]:
        """Extract all operators used in expression"""
        operators = set()

        # Explicit operator symbols
        operator_symbols = {
            '+': 'addition',
            '-': 'subtraction',
            '*': 'multiplication',
            '×': 'multiplication',
            '·': 'multiplication',  # Middle dot
            '/': 'division',
            '^': 'exponentiation',
            '²': 'square',
            '³': 'cube',
            '→': 'transformation',
            '←': 'reverse_transformation',
            '↔': 'bidirectional',
            '⊕': 'exclusive_or',
            '⊗': 'tensor_product',
            '⊙': 'hadamard',
            '∧': 'conjunction',
            '∨': 'disjunction',
            '¬': 'negation',
            '√': 'square_root',
            '∫': 'integration',
            '∂': 'partial_derivative',
            '∑': 'summation',
            'Σ': 'summation',
            '∏': 'product',
            '∈': 'element_of',
            '∀': 'for_all',
            '∃': 'exists',
            '∇': 'gradient',
            '?': 'ternary',
            ':': 'ternary',
            '>': 'comparison',
            '<': 'comparison',
            '≥': 'comparison',
            '≤': 'comparison',
            '≈': 'approximate',
            '~': 'sample',
            '=': 'identity',  # Assignment/identity is an operator
        }

        for symbol, name in operator_symbols.items():
            if symbol in expression:
                operators.add(symbol)

        # Function application: f(...), func_name(...)
        if re.search(r'[a-zA-Z_][a-zA-Z0-9_]*\s*\([^)]*\)', expression):
            operators.add('()')

        # Quantum/bra-ket notation: |ψ⟩, ⟨ψ|, M̂|ψ⟩
        if '|' in expression and ('⟩' in expression or '⟨' in expression or '>' in expression):
            operators.add('|⟩')

        # Hat operators: Ĥ, M̂ (precomposed circumflex)
        circumflex_letters = 'ÂĈÊĜĤÎĴÔŜÛŴŶâĉêĝĥîĵôŝûŵŷ'
        if '̂' in expression or any(c in expression for c in circumflex_letters):
            operators.add('^')

        # Implicit multiplication: (a)(b)
        if re.search(r'\)\s*\(', expression):
            operators.add('×')

        # Text-based logical operators
        if ' AND ' in expression or ' and ' in expression:
            operators.add('∧')
        if ' OR ' in expression or ' or ' in expression:
            operators.add('∨')
        if ' NOT ' in expression or ' not ' in expression:
            operators.add('¬')

        return operators
    
    def _extract_consciousness_level(self, text: str) -> Optional[str]:
        """Extract consciousness level annotation like [S3]"""
        match = re.search(r'\[S(\d+)\]', text)
        if match:
            return f"S{match.group(1)}"
        return None
    
    def _print_formula_summary(self):
        """Print formula parsing statistics"""
        print("\n" + "="*60)
        print("FORMULA PARSING SUMMARY")
        print("="*60)
        print(f"Total formulas parsed: {len(self.formulas)}")
        
        # Count by consciousness level
        level_counts = defaultdict(int)
        for formula in self.formulas:
            level = formula['consciousness_level'] or 'None'
            level_counts[level] += 1
        
        print("\nBy consciousness level:")
        for level in sorted(level_counts.keys()):
            print(f"  {level}: {level_counts[level]}")
        
        # Show first 5 formulas as examples
        print("\nFirst 5 formulas:")
        for i, formula in enumerate(self.formulas[:5], 1):
            print(f"  {i}. {formula['name']} = {formula['expression'][:50]}...")
        
        print("="*60 + "\n")

# ============================================================================
    # STEP 3: BUILD VARIABLE REGISTRY
    # ============================================================================
    
    def build_variable_registry(self):
        """Create master list of all variables and classify them"""
        print("\nBuilding variable registry...")
        
        # Collect all variables
        all_variables = set()
        
        # Add output variables (things being defined)
        for formula in self.formulas:
            all_variables.add(formula['name'])
        
        # Add input variables (things being used)
        for formula in self.formulas:
            for var in formula['variables_used']:
                all_variables.add(var)
        
        print(f"Found {len(all_variables)} unique variables")
        
        # Classify each variable
        for var_name in all_variables:
            self._classify_variable(var_name)
        
        # Identify the 25 core operators
        self._identify_operators()
        
        self._print_variable_summary()
    
    def _classify_variable(self, var_name: str):
        """Classify a variable as primitive, derived, or operator"""
        # Find formulas that define this variable
        defined_in = []
        for formula in self.formulas:
            if formula['name'] == var_name:
                defined_in.append(formula['id'])
        
        # Find formulas that use this variable
        used_in = []
        for formula in self.formulas:
            if var_name in formula['variables_used']:
                used_in.append(formula['id'])
        
        # Determine type
        if len(defined_in) == 0:
            var_type = 'primitive'  # Never defined = input variable
        elif len(defined_in) >= 1:
            var_type = 'derived'  # Defined = calculated variable
        else:
            var_type = 'unknown'
        
        # Check if it's a known operator
        if self._is_operator_name(var_name):
            var_type = 'operator'
        
        # Store in registry
        self.variables[var_name] = {
            'name': var_name,
            'type': var_type,
            'defined_in': defined_in,
            'used_in': used_in,
            'sanskrit_name': self._extract_sanskrit_name(var_name),
            'english_translation': self._translate_to_english(var_name)
        }
    
    def _is_operator_name(self, name: str) -> bool:
        """Check if variable name matches known OOF operators"""
        # The 25 core operators (approximate list - will refine)
        core_operators = {
            'Consciousness', 'Ψ', 'Psi',
            'Karma', 'K',
            'Maya', 'M',
            'Time', 'T',
            'Space', 'S',
            'Witness', 'W',
            'Grace', 'G',
            'Prana', 'P',
            'Shakti',
            'Void', 'V',
            'Love', 'L',
            'Awareness', 'A',
            'Entropy', 'E',
            'Resonance', 'R',
            'Creator', 'C',
            'Seva',
            'Attachment',
            'Cleaning',
            'Surrender',
            'Aspiration',
            'Fear',
            'Desire',
            'Kama',
            'Buddhi',
            'Manas',
            'Chitta'
        }
        
        return name in core_operators
    
    def _extract_sanskrit_name(self, name: str) -> Optional[str]:
        """Map English name to Sanskrit if applicable"""
        # Basic mapping (will expand)
        sanskrit_map = {
            'Consciousness': 'Chit',
            'Witness': 'Sakshi',
            'Grace': 'Anugraha',
            'Desire': 'Kama',
            'Intellect': 'Buddhi',
            'Mind': 'Manas',
            'Memory': 'Chitta',
            'Love': 'Prema',
            'Service': 'Seva',
            'Energy': 'Prana',
            'Power': 'Shakti',
            'Illusion': 'Maya',
            'Action': 'Karma',
            'Void': 'Shunya'
        }
        
        return sanskrit_map.get(name, None)
    
    def _translate_to_english(self, name: str) -> str:
        """Translate Sanskrit/technical terms to plain English"""
        # Reverse mapping
        english_map = {
            'Ψ': 'Consciousness',
            'K': 'Karma',
            'M': 'Maya',
            'T': 'Time',
            'S': 'Space',
            'W': 'Witness',
            'G': 'Grace',
            'P': 'Prana',
            'V': 'Void',
            'L': 'Love',
            'A': 'Awareness',
            'E': 'Entropy',
            'R': 'Resonance',
            'C': 'Creator',
            'Kama': 'Desire',
            'Buddhi': 'Intellect',
            'Manas': 'Mind',
            'Chitta': 'Memory',
            'Prema': 'Love',
            'Seva': 'Service',
            'Shakti': 'Power',
            'Shunya': 'Void',
            'Sakshi': 'Witness',
            'Anugraha': 'Grace',
            'Chit': 'Consciousness'
        }
        
        return english_map.get(name, name)
    
    def _identify_operators(self):
        """Extract the 25 core operators from variable registry"""
        operator_vars = {k: v for k, v in self.variables.items() 
                        if v['type'] == 'operator'}
        
        self.operators = []
        for name, var_info in operator_vars.items():
            operator_obj = {
                'name': name,
                'sanskrit': var_info['sanskrit_name'],
                'english': var_info['english_translation'],
                'defined_in': var_info['defined_in'],
                'used_in': var_info['used_in'],
                'usage_count': len(var_info['used_in'])
            }
            self.operators.append(operator_obj)
        
        # Sort by usage count
        self.operators.sort(key=lambda x: x['usage_count'], reverse=True)
    
    def _print_variable_summary(self):
        """Print variable registry statistics"""
        print("\n" + "="*60)
        print("VARIABLE REGISTRY SUMMARY")
        print("="*60)
        print(f"Total unique variables: {len(self.variables)}")
        
        # Count by type
        type_counts = defaultdict(int)
        for var in self.variables.values():
            type_counts[var['type']] += 1
        
        print("\nBy type:")
        for var_type, count in sorted(type_counts.items()):
            print(f"  {var_type}: {count}")
        
        # Show top operators by usage
        print(f"\nTop 10 operators by usage:")
        for i, op in enumerate(self.operators[:10], 1):
            print(f"  {i}. {op['name']} ({op['english']}) - used in {op['usage_count']} formulas")
        
        # Show sample primitives
        primitives = [v for v in self.variables.values() if v['type'] == 'primitive']
        print(f"\nSample primitives (first 10 of {len(primitives)}):")
        for i, prim in enumerate(primitives[:10], 1):
            print(f"  {i}. {prim['name']}")
        
        print("="*60 + "\n")

        # ============================================================================
    # STEP 4: EXTRACT DEPENDENCIES
    # ============================================================================
    
    def extract_dependencies(self):
        """Map which formulas depend on which other formulas"""
        print("\nExtracting dependencies...")
        
        # Build formula lookup by name
        formula_by_name = {}
        for formula in self.formulas:
            formula_by_name[formula['name']] = formula
        
        # For each formula, find its dependencies
        for formula in self.formulas:
            dependencies = set()
            
            # Look at each variable it uses
            for var_name in formula['variables_used']:
                # Find which formula defines this variable
                var_info = self.variables.get(var_name)
                
                if var_info and var_info['type'] == 'derived':
                    # This variable is defined by another formula
                    for defining_formula_id in var_info['defined_in']:
                        # Don't add self-dependency
                        if defining_formula_id != formula['id']:
                            dependencies.add(defining_formula_id)
            
            # Store dependencies
            formula['dependencies'] = list(dependencies)
            
            # Store in dependency graph
            self.dependencies[formula['id']] = {
                'formula_name': formula['name'],
                'depends_on': list(dependencies),
                'depended_on_by': []  # Will fill in second pass
            }
        
        # Second pass: fill in depended_on_by
        for formula in self.formulas:
            for dep_id in formula['dependencies']:
                if dep_id in self.dependencies:
                    self.dependencies[dep_id]['depended_on_by'].append(formula['id'])
        
        # Check for circular dependencies
        circular_deps = self._detect_circular_dependencies()
        
        if circular_deps:
            print(f"⚠ WARNING: Found {len(circular_deps)} circular dependency chains")
            self.metadata['parsing_warnings'].append(
                f"Circular dependencies detected: {len(circular_deps)} chains"
            )
        
        self._print_dependency_summary(circular_deps)
    
    def _detect_circular_dependencies(self) -> List[List[int]]:
        """Detect circular dependencies using depth-first search"""
        circular_chains = []
        visited = set()
        rec_stack = {}  # Maps formula_id -> path to that formula
        
        def dfs(formula_id: int, path: List[int]):
            """Detect cycles in dependency graph"""
            if formula_id in rec_stack:
                # Found a cycle - construct it
                cycle_start_idx = None
                for i, fid in enumerate(path):
                    if fid == formula_id:
                        cycle_start_idx = i
                        break
                
                if cycle_start_idx is not None:
                    cycle = path[cycle_start_idx:] + [formula_id]
                    # Avoid duplicates
                    if cycle not in circular_chains:
                        circular_chains.append(cycle)
                return
            
            if formula_id in visited:
                return
            
            visited.add(formula_id)
            rec_stack[formula_id] = path.copy()
            
            # Check all dependencies
            if formula_id in self.dependencies:
                for dep_id in self.dependencies[formula_id]['depends_on']:
                    dfs(dep_id, path + [formula_id])
            
            # Remove from recursion stack when done
            if formula_id in rec_stack:
                del rec_stack[formula_id]
        
        # Check each formula
        for formula in self.formulas:
            if formula['id'] not in visited:
                dfs(formula['id'], [])
        
        return circular_chains
    
    def _print_dependency_summary(self, circular_deps: List[List[int]]):
        """Print dependency statistics"""
        print("\n" + "="*60)
        print("DEPENDENCY EXTRACTION SUMMARY")
        print("="*60)
        print(f"Total formulas: {len(self.formulas)}")
        
        # Count dependency statistics
        no_deps = sum(1 for f in self.formulas if len(f['dependencies']) == 0)
        has_deps = len(self.formulas) - no_deps
        
        avg_deps = sum(len(f['dependencies']) for f in self.formulas) / len(self.formulas)
        max_deps = max(len(f['dependencies']) for f in self.formulas)
        
        print(f"\nFormulas with no dependencies: {no_deps}")
        print(f"Formulas with dependencies: {has_deps}")
        print(f"Average dependencies per formula: {avg_deps:.2f}")
        print(f"Maximum dependencies: {max_deps}")
        
        # Find most depended-on formulas
        dep_counts = []
        for formula_id, dep_info in self.dependencies.items():
            dep_counts.append({
                'id': formula_id,
                'name': dep_info['formula_name'],
                'count': len(dep_info['depended_on_by'])
            })
        
        dep_counts.sort(key=lambda x: x['count'], reverse=True)
        
        print("\nMost depended-on formulas (top 10):")
        for i, item in enumerate(dep_counts[:10], 1):
            print(f"  {i}. {item['name']} - used by {item['count']} formulas")
        
        # Show circular dependencies if any
        if circular_deps:
            print(f"\n⚠ CIRCULAR DEPENDENCIES DETECTED: {len(circular_deps)} chains")
            print("First 5 circular chains:")
            for i, chain in enumerate(circular_deps[:5], 1):
                chain_names = []
                for formula_id in chain:
                    if formula_id in self.dependencies:
                        chain_names.append(self.dependencies[formula_id]['formula_name'])
                print(f"  {i}. {' → '.join(chain_names)}")
        else:
            print("\n✓ No circular dependencies detected")
        
        print("="*60 + "\n")

# ============================================================================
    # STEP 5: ASSIGN TIERS
    # ============================================================================
    
    def assign_tiers(self):
        """Organize formulas into execution tiers"""
        print("\nAssigning execution tiers...")
        
        # Mark circular dependency formulas first
        circular_formula_ids = set()
        circular_deps = self._detect_circular_dependencies()
        
        for chain in circular_deps:
            for formula_id in chain:
                circular_formula_ids.add(formula_id)
        
        print(f"Found {len(circular_formula_ids)} formulas in circular dependencies")
        
        # Assign tiers
        unassigned = set(f['id'] for f in self.formulas if f['id'] not in circular_formula_ids)
        current_tier = 0
        max_iterations = 100  # Prevent infinite loop
        iteration = 0
        
        while unassigned and iteration < max_iterations:
            assigned_this_tier = []
            
            for formula_id in unassigned:
                formula = next(f for f in self.formulas if f['id'] == formula_id)
                
                # Check if all dependencies are satisfied
                all_deps_satisfied = True
                
                for dep_id in formula['dependencies']:
                    # Skip if dependency is in circular chain
                    if dep_id in circular_formula_ids:
                        continue
                    
                    # Find the dependency formula
                    dep_formula = next((f for f in self.formulas if f['id'] == dep_id), None)
                    
                    if dep_formula is None:
                        # Dependency not found - treat as primitive
                        continue
                    
                    if dep_formula['tier'] is None or dep_formula['tier'] >= current_tier:
                        all_deps_satisfied = False
                        break
                
                if all_deps_satisfied:
                    formula['tier'] = current_tier
                    assigned_this_tier.append(formula_id)
            
            # Remove assigned formulas
            for formula_id in assigned_this_tier:
                unassigned.remove(formula_id)
            
            # Move to next tier if we made progress
            if assigned_this_tier:
                print(f"  Tier {current_tier}: {len(assigned_this_tier)} formulas")
                current_tier += 1
            else:
                # No progress - remaining formulas must have unresolved dependencies
                if unassigned:
                    print(f"  ⚠ {len(unassigned)} formulas couldn't be assigned (complex dependencies)")
                    # Assign them to a special tier
                    for formula_id in unassigned:
                        formula = next(f for f in self.formulas if f['id'] == formula_id)
                        formula['tier'] = 999  # Special "unresolved" tier
                break
            
            iteration += 1
        
        # Assign circular dependency formulas to special tier -1 (iterative)
        for formula_id in circular_formula_ids:
            formula = next(f for f in self.formulas if f['id'] == formula_id)
            formula['tier'] = -1
        
        print(f"  Tier -1 (iterative): {len(circular_formula_ids)} formulas")
        
        self._print_tier_summary()
    
    def _print_tier_summary(self):
        """Print tier assignment statistics"""
        print("\n" + "="*60)
        print("TIER ASSIGNMENT SUMMARY")
        print("="*60)
        
        # Count formulas by tier
        tier_counts = defaultdict(int)
        for formula in self.formulas:
            tier = formula['tier']
            if tier is not None:
                tier_counts[tier] += 1
            else:
                tier_counts['None'] += 1
        
        # Sort tiers
        sorted_tiers = sorted([t for t in tier_counts.keys() if t != 'None'])
        
        print("Formula distribution by tier:")
        
        # Show special tiers first
        if -1 in tier_counts:
            print(f"  Tier -1 (iterative/circular): {tier_counts[-1]} formulas")
        
        # Show normal tiers
        for tier in sorted_tiers:
            if tier >= 0 and tier < 900:
                print(f"  Tier {tier}: {tier_counts[tier]} formulas")
        
        # Show unresolved
        if 999 in tier_counts:
            print(f"  Tier 999 (unresolved): {tier_counts[999]} formulas")
        
        if 'None' in tier_counts:
            print(f"  Not assigned: {tier_counts['None']} formulas")
        
        # Calculate max tier
        max_tier = max([t for t in tier_counts.keys() if isinstance(t, int) and t < 900], default=0)
        print(f"\nMaximum tier depth: {max_tier}")
        
        # Show sample formulas from each tier
        print("\nSample formulas by tier:")
        for tier in sorted(set(t for t in tier_counts.keys() if isinstance(t, int) and t >= -1 and t < 900))[:5]:
            tier_formulas = [f for f in self.formulas if f['tier'] == tier]
            if tier_formulas:
                sample = tier_formulas[0]
                print(f"  Tier {tier}: {sample['name']} = {sample['expression'][:60]}...")
        
        print("="*60 + "\n")

# ============================================================================
    # STEP 6: PARSE CONFIDENCE RULES
    # ============================================================================
    
    def parse_confidence_rules(self):
        """Extract uncertainty propagation logic from OOF_Math.txt"""
        print("\nParsing confidence rules...")
        
        # Initialize confidence rules structure
        self.confidence_rules = {
            'operator_rules': {},
            'level_thresholds': {},
            'minimum_confidence': 0.3,
            'default_confidence': 1.0
        }
        
        # Define default operator confidence functions
        default_operator_rules = {
            '*': {'function': 'multiply', 'description': 'C_result = C_a × C_b'},
            '×': {'function': 'multiply', 'description': 'C_result = C_a × C_b'},
            '+': {'function': 'minimum', 'description': 'C_result = min(C_a, C_b)'},
            '-': {'function': 'minimum', 'description': 'C_result = min(C_a, C_b)'},
            '/': {'function': 'divide', 'description': 'C_result = C_a / (C_b + ε)'},
            '^': {'function': 'exponential_decay', 'description': 'C_result = C_a^C_b'},
            '→': {'function': 'minimum', 'description': 'C_result = min(C_a, C_b)'},
            '←': {'function': 'minimum', 'description': 'C_result = min(C_a, C_b)'},
            '↔': {'function': 'multiply', 'description': 'C_result = C_a × C_b'},
        }
        
        self.confidence_rules['operator_rules'] = default_operator_rules
        
        # Define consciousness level thresholds
        self.confidence_rules['level_thresholds'] = {
            'S1_to_S2': 0.7,
            'S2_to_S3': 0.75,
            'S3_to_S4': 0.8,
            'S4_to_S5': 0.85,
            'S5_to_S6': 0.9,
            'S6_to_S7': 0.95,
            'S7_to_S8': 0.98
        }
        
        # Search for confidence-related content in original file
        confidence_mentions = 0
        for line in self.lines:
            if line['type'] in ['DOCUMENTATION', 'COMMENT']:
                text_lower = line['text'].lower()
                if any(word in text_lower for word in ['confidence', 'certainty', 'uncertainty', 'probability']):
                    confidence_mentions += 1
        
        print(f"Found {confidence_mentions} confidence-related mentions in documentation")
        print("✓ Applied default confidence propagation rules")
    
    # ============================================================================
    # STEP 7: GENERATE REGISTRY.JSON
    # ============================================================================
    
    def generate_registry(self):
        """Package everything into registry.json"""
        print("\nGenerating registry.json...")
        
        # Update metadata
        self.metadata['end_time'] = datetime.now().isoformat()
        self.metadata['total_formulas'] = len(self.formulas)
        self.metadata['total_variables'] = len(self.variables)
        self.metadata['total_operators'] = len(self.operators)
        
        # Calculate max tier
        max_tier = max([f['tier'] for f in self.formulas if f['tier'] is not None and f['tier'] < 900], default=0)
        self.metadata['max_tier'] = max_tier
        
        # Build tier distribution
        tier_distribution = defaultdict(int)
        for formula in self.formulas:
            tier = formula['tier']
            if tier is not None:
                tier_distribution[str(tier)] = tier_distribution.get(str(tier), 0) + 1
        
        # Build complete registry structure
        registry = {
            'metadata': self.metadata,
            'formulas': self.formulas,
            'variables': self.variables,
            'operators': self.operators,
            'confidence_rules': self.confidence_rules,
            'tier_distribution': dict(tier_distribution),
            'dependencies': self.dependencies
        }
        
        # Write to file
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(registry, f, indent=2, ensure_ascii=False)
        
        # Get file size
        file_size = os.path.getsize(self.output_file)
        file_size_mb = file_size / (1024 * 1024)
        
        print(f"✓ Registry written to {self.output_file}")
        print(f"  File size: {file_size_mb:.2f} MB")
    
    # ============================================================================
    # STEP 8: VALIDATE REGISTRY
    # ============================================================================
    
    def validate_registry(self):
        """Validate the generated registry"""
        print("\nValidating registry...")
        
        errors = []
        warnings = []
        
        # 1. Completeness checks
        if len(self.formulas) < 1000:
            warnings.append(f"Formula count ({len(self.formulas)}) lower than expected (~1,100+)")
        
        if len(self.operators) < 20:
            warnings.append(f"Operator count ({len(self.operators)}) lower than expected (25)")
        
        # 2. Dependency integrity
        for formula in self.formulas:
            for dep_id in formula['dependencies']:
                if dep_id not in [f['id'] for f in self.formulas]:
                    errors.append(f"Formula {formula['id']} references non-existent dependency {dep_id}")
        
        # 3. Tier assignment
        unassigned = [f for f in self.formulas if f['tier'] is None]
        if unassigned:
            warnings.append(f"{len(unassigned)} formulas without tier assignment")
        
        # 4. Circular dependencies
        circular_count = len([f for f in self.formulas if f['tier'] == -1])
        if circular_count > 0:
            warnings.append(f"{circular_count} formulas in circular dependencies (will need iterative solving)")
        
        # 5. Variable references
        for formula in self.formulas:
            for var in formula['variables_used']:
                if var not in self.variables:
                    warnings.append(f"Formula {formula['id']} uses undefined variable: {var}")
        
        # 6. Confidence rules
        if not self.confidence_rules.get('operator_rules'):
            errors.append("No operator confidence rules defined")
        
        # Print validation results
        print("\n" + "="*60)
        print("VALIDATION RESULTS")
        print("="*60)
        
        if errors:
            print(f"\n❌ ERRORS ({len(errors)}):")
            for error in errors[:10]:
                print(f"  - {error}")
            if len(errors) > 10:
                print(f"  ... and {len(errors) - 10} more")
        else:
            print("\n✓ No critical errors")
        
        if warnings:
            print(f"\n⚠ WARNINGS ({len(warnings)}):")
            for warning in warnings[:10]:
                print(f"  - {warning}")
            if len(warnings) > 10:
                print(f"  ... and {len(warnings) - 10} more")
        else:
            print("\n✓ No warnings")
        
        # Summary statistics
        print("\nSUMMARY STATISTICS:")
        print(f"  Total formulas: {len(self.formulas)}")
        print(f"  Total variables: {len(self.variables)}")
        print(f"  Total operators: {len(self.operators)}")
        print(f"  Max tier depth: {self.metadata.get('max_tier', 'unknown')}")
        print(f"  Circular formulas: {circular_count}")
        print(f"  Validation status: {'❌ FAILED' if errors else '✅ PASSED'}")
        
        print("="*60 + "\n")
        
        return len(errors) == 0

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    INPUT_FILE = './OOF_Math.txt'
    OUTPUT_FILE = './registry.json'
    
    compiler = FormulaCompiler(INPUT_FILE, OUTPUT_FILE)
    
    print("="*60)
    print("OOF FORMULA COMPILER")
    print("="*60)
    print(f"Input:  {INPUT_FILE}")
    print(f"Output: {OUTPUT_FILE}")
    print("="*60 + "\n")
    
    # Step 1: Load file
    if not compiler.load_file():
        print("❌ Failed to load file. Exiting.")
        return
    print("✓ Step 1 complete: File loaded and classified\n")
    
    # Step 2: Parse formulas
    compiler.parse_formulas()
    print("✓ Step 2 complete: Formulas parsed\n")
    
    # Step 3: Build variable registry
    compiler.build_variable_registry()
    print("✓ Step 3 complete: Variable registry built\n")
    
    # Step 4: Extract dependencies
    compiler.extract_dependencies()
    print("✓ Step 4 complete: Dependencies extracted\n")
    
    # Step 5: Assign tiers
    compiler.assign_tiers()
    print("✓ Step 5 complete: Tiers assigned\n")
    
    # Step 6: Parse confidence rules
    compiler.parse_confidence_rules()
    print("✓ Step 6 complete: Confidence rules parsed\n")
    
    # Step 7: Generate registry
    compiler.generate_registry()
    print("✓ Step 7 complete: Registry generated\n")
    
    # Step 8: Validate
    success = compiler.validate_registry()
    print("✓ Step 8 complete: Validation finished\n")
    
    # Final summary
    print("="*60)
    print("COMPILATION COMPLETE")
    print("="*60)
    if success:
        print("✅ Registry successfully compiled and validated")
        print(f"📄 Output: {OUTPUT_FILE}")
    else:
        print("⚠ Registry compiled with errors - review validation output")
    print("="*60)


if __name__ == '__main__':
    main()


if __name__ == '__main__':
    main()