"""
Rule List View
Browse all rules in sequence order
"""
import streamlit as st
import pandas as pd
from typing import Dict
from utils.joins import get_rules_with_stats

def render_rule_list(tables: Dict[str, pd.DataFrame]):
    """Render the rule list view"""
    
    st.title("📋 Rule List")
    
    # Get rules with statistics
    rules_df = get_rules_with_stats(tables)

    if len(rules_df) == 0:
        st.warning("No rules found")
        return

    # Parse RULE_TYPE from Rule column (first 2 chars of rule ID)
    rules_df['RULE_TYPE'] = rules_df['Rule'].str[:2]

    # Filters
    col1, col2, col3 = st.columns(3)

    with col1:
        rule_types = ['All'] + sorted(rules_df['RULE_TYPE'].unique().tolist())
        selected_type = st.selectbox("Filter by Type", rule_types)
    
    with col2:
        search_term = st.text_input("Search Rule Name/ID")
    
    with col3:
        sort_by = st.selectbox("Sort By", ["Sequence", "Rule Name", "Rule Type"])
    
    # Apply filters
    filtered_df = rules_df.copy()
    
    if selected_type != 'All':
        filtered_df = filtered_df[filtered_df['RULE_TYPE'] == selected_type]
    
    if search_term:
        mask = (
            filtered_df['Rule'].str.contains(search_term, case=False, na=False) |
            filtered_df['Dsgn Bldr Scrpt Prcs'].str.contains(search_term, case=False, na=False)
        )
        filtered_df = filtered_df[mask]

    # Sort
    if sort_by == "Sequence":
        filtered_df = filtered_df.sort_values('Processing Sequence')
    elif sort_by == "Rule Name":
        filtered_df = filtered_df.sort_values('Dsgn Bldr Scrpt Prcs')
    else:
        filtered_df = filtered_df.sort_values('RULE_TYPE')
    
    # Display count
    st.info(f"📊 Showing {len(filtered_df)} of {len(rules_df)} rules")
    
    # Format rule type labels
    type_labels = {
        '01': '01-Selection',
        '02': '02-SubProcess',
        '03': '03-Function',
        '04': '04-Classification'
    }
    
    # Prepare display dataframe
    display_df = filtered_df[[
        'Processing Sequence', 'Rule', 'RULE_TYPE', 'Dsgn Bldr Scrpt Prcs',
        'condition_count', 'output_count'
    ]].copy()

    display_df['RULE_TYPE'] = display_df['RULE_TYPE'].map(type_labels)
    
    display_df.columns = [
        'Sequence', 'Rule ID', 'Type', 'Rule Name', 
        '# Conditions', '# Outputs'
    ]
    
    # Color code by type
    def color_type(val):
        if '01-' in val:
            return 'background-color: #e3f2fd'
        elif '02-' in val:
            return 'background-color: #e8f5e9'
        elif '03-' in val:
            return 'background-color: #fff3e0'
        elif '04-' in val:
            return 'background-color: #f3e5f5'
        return ''
    
    # Display table with click interaction
    st.dataframe(
        display_df.style.applymap(color_type, subset=['Type']),
        use_container_width=True,
        height=600
    )
    
    # Rule selection for detail view
    st.divider()
    
    rule_ids = filtered_df['Rule'].tolist()
    selected_rule = st.selectbox(
        "Select a rule to view details:",
        rule_ids,
        format_func=lambda x: f"{x} - {filtered_df[filtered_df['Rule']==x].iloc[0]['Dsgn Bldr Scrpt Prcs']}"
    )
    
    if st.button("View Rule Details", use_container_width=True):
        st.session_state['current_view'] = 'rule_detail'
        st.session_state['selected_rule'] = selected_rule
        st.rerun()
