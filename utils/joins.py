"""
Common data join operations for Product Category Browser
"""
import pandas as pd
from typing import Dict

def get_rules_with_stats(tables: Dict[str, pd.DataFrame], 
                         prod_categ: str = None) -> pd.DataFrame:
    """
    Get all rules with statistics (condition count, output count, etc.)
    
    Args:
        tables: Dictionary of loaded tables
        prod_categ: Optional filter for product category
        
    Returns:
        DataFrame with rule information and statistics
    """
    rules = tables['zpd_script_dtl'].copy()

    # Filter by category if specified
    if prod_categ:
        rules = rules[rules['PrdCat'] == prod_categ]
    
    # Add condition counts
    if 'zpd_script_con' in tables:
        cond_counts = tables['zpd_script_con'].groupby('Rule').size().reset_index(name='condition_count')
        rules = rules.merge(cond_counts, left_on='Rule', right_on='Rule', how='left')
        rules['condition_count'] = rules['condition_count'].fillna(0).astype(int)
    else:
        rules['condition_count'] = 0
    
    # Add output counts (for Type 01 rules)
    if 'zpd_slrule_def' in tables:
        output_counts = tables['zpd_slrule_def'][tables['zpd_slrule_def']['Character Length 1'] == 'O'].groupby('Rule').size().reset_index(name='output_count')
        rules = rules.merge(output_counts, on='Rule', how='left')
        rules['output_count'] = rules['output_count'].fillna(0).astype(int)
    else:
        rules['output_count'] = 0

    # Sort by sequence
    rules = rules.sort_values('Processing Sequence')
    
    return rules


def get_rule_details(tables: Dict[str, pd.DataFrame], rule_id: str) -> Dict:
    """
    Get complete details for a single rule
    
    Args:
        tables: Dictionary of loaded tables
        rule_id: Rule ID to retrieve
        
    Returns:
        Dictionary with rule details including conditions, inputs, outputs, etc.
    """
    result = {}
    
    # Get rule header
    rules = tables['zpd_script_dtl']
    rule = rules[rules['Rule'] == rule_id]
    if len(rule) == 0:
        return None

    result['header'] = rule.iloc[0].to_dict()

    # Get conditions
    if 'zpd_script_con' in tables:
        conditions = tables['zpd_script_con'][tables['zpd_script_con']['Rule'] == rule_id]
        result['conditions'] = conditions.to_dict('records')
    else:
        result['conditions'] = []

    # Get input/output definitions (for Type 01)
    if 'zpd_slrule_def' in tables:
        slrule_def = tables['zpd_slrule_def'][tables['zpd_slrule_def']['Rule'] == rule_id]
        result['inputs'] = slrule_def[slrule_def['Character Length 1'] == 'I'].to_dict('records')
        result['outputs'] = slrule_def[slrule_def['Character Length 1'] == 'O'].to_dict('records')
    else:
        result['inputs'] = []
        result['outputs'] = []

    # Get output values (for Type 01)
    if 'zpd_slrule_val' in tables:
        values = tables['zpd_slrule_val'][tables['zpd_slrule_val']['Rule'] == rule_id]
        result['values'] = values.to_dict('records')
    else:
        result['values'] = []

    # Get transactions (for Type 01)
    if 'zpd_slrule_opt' in tables:
        transactions = tables['zpd_slrule_opt'][tables['zpd_slrule_opt']['Rule'] == rule_id]
        result['transactions'] = transactions.to_dict('records')
    else:
        result['transactions'] = []

    # Get sub-process links (for Type 02)
    if 'zpd_shar_rule' in tables:
        subprocs = tables['zpd_shar_rule'][tables['zpd_shar_rule']['Rule'] == rule_id]
        result['subprocesses'] = subprocs.to_dict('records')
    else:
        result['subprocesses'] = []
    
    return result


def get_fields_set(tables: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Get list of all unique fields that are set (outputs)
    
    Args:
        tables: Dictionary of loaded tables
        
    Returns:
        DataFrame with field names and statistics
    """
    if 'zpd_slrule_def' not in tables:
        return pd.DataFrame(columns=['Char. Name', 'rule_count'])

    outputs = tables['zpd_slrule_def'][tables['zpd_slrule_def']['Character Length 1'] == 'O']

    field_stats = outputs.groupby('Char. Name').agg(
        rule_count=('Rule', 'nunique')
    ).reset_index()

    field_stats = field_stats.sort_values('Char. Name')
    
    return field_stats


def get_rules_for_field(tables: Dict[str, pd.DataFrame], field_name: str) -> pd.DataFrame:
    """
    Get all rules that set a specific field
    
    Args:
        tables: Dictionary of loaded tables
        field_name: Field/characteristic name
        
    Returns:
        DataFrame with rules that set this field
    """
    if 'zpd_slrule_def' not in tables:
        return pd.DataFrame()

    # Get rules that output this field
    outputs = tables['zpd_slrule_def'][
        (tables['zpd_slrule_def']['Character Length 1'] == 'O') &
        (tables['zpd_slrule_def']['Char. Name'] == field_name)
    ]

    # Join with rule details
    rules = tables['zpd_script_dtl']
    result = outputs.merge(rules, on='Rule', how='left')

    # Get values for this field
    if 'zpd_slrule_val' in tables:
        values = tables['zpd_slrule_val'][tables['zpd_slrule_val']['Char. Name'] == field_name]

        # Group values by rule
        value_summary = values.groupby('Rule').apply(
            lambda x: ', '.join([f"Row {row['Row']}: {row.get('Characteristic Value', row.get('Val from', ''))}"
                                for _, row in x.iterrows()])
        ).reset_index(name='values_set')

        result = result.merge(value_summary, on='Rule', how='left')

    result = result.sort_values('Processing Sequence')
    
    return result


def get_field_dependencies(tables: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Get field dependency information (which fields depend on which)
    
    Args:
        tables: Dictionary of loaded tables
        
    Returns:
        DataFrame showing field dependencies
    """
    if 'zpd_slrule_def' not in tables:
        return pd.DataFrame()
    
    slrule_def = tables['zpd_slrule_def']

    # Get inputs and outputs per rule
    inputs = slrule_def[slrule_def['Character Length 1'] == 'I'][['Rule', 'Char. Name']].rename(columns={'Char. Name': 'input_field'})
    outputs = slrule_def[slrule_def['Character Length 1'] == 'O'][['Rule', 'Char. Name']].rename(columns={'Char. Name': 'output_field'})

    # Join to create dependencies
    deps = outputs.merge(inputs, on='Rule', how='inner')
    
    # Aggregate by field pairs
    field_deps = deps.groupby(['output_field', 'input_field']).size().reset_index(name='rule_count')
    field_deps = field_deps[field_deps['output_field'] != field_deps['input_field']]  # Exclude self-references
    
    return field_deps
