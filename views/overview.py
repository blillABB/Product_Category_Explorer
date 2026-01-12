"""
Category Overview Dashboard
Shows high-level summary of the product category
"""
import streamlit as st
import pandas as pd
from typing import Dict

def render_overview(tables: Dict[str, pd.DataFrame]):
    """Render the category overview dashboard"""
    
    st.title("📊 Product Category Overview")
    
    # Get category info
    if 'zpd_prd_categ' not in tables:
        st.error("Category master data not available")
        return
    
    cat_info = tables['zpd_prd_categ'].iloc[0]
    
    # Header info
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Category", cat_info['PrdCat'])
    with col2:
        st.metric("Type", cat_info['Cat Type'])
    with col3:
        st.metric("Dataset", cat_info['DS'])
    with col4:
        if 'Ver. No.' in cat_info:
            st.metric("Version", cat_info['Ver. No.'])
    
    st.divider()
    
    # Rule statistics
    if 'zpd_script_dtl' not in tables:
        st.warning("No rule data available")
        return
    
    rules = tables['zpd_script_dtl']
    
    st.subheader("📋 Rule Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Rules", len(rules))
    
    with col2:
        seq_min = rules['Processing Sequence'].min()
        seq_max = rules['Processing Sequence'].max()
        st.metric("Sequence Range", f"{seq_min} - {seq_max}")
    
    with col3:
        if 'zpd_script_con' in tables:
            condition_count = len(tables['zpd_script_con'])
            st.metric("Total Conditions", condition_count)
        else:
            st.metric("Total Conditions", "N/A")
    
    with col4:
        if 'zpd_slrule_def' in tables:
            unique_fields = tables['zpd_slrule_def']['Char. Name'].nunique()
            st.metric("Unique Fields", unique_fields)
        else:
            st.metric("Unique Fields", "N/A")
    
    # Rule type breakdown
    st.subheader("🔢 Rules by Type")
    
    type_labels = {
        '01': 'Selection',
        '02': 'Sub-Process',
        '03': 'Function Call',
        '04': 'Classification'
    }
    
    # Parse RULE_TYPE from Rule column (first 2 chars of rule ID)
    rules['RULE_TYPE'] = rules['Rule'].str[:2]
    type_counts = rules['RULE_TYPE'].value_counts().sort_index()
    
    col1, col2, col3, col4 = st.columns(4)
    cols = [col1, col2, col3, col4]
    
    for idx, (rule_type, count) in enumerate(type_counts.items()):
        with cols[idx % 4]:
            label = type_labels.get(rule_type, f"Type {rule_type}")
            st.metric(label, count)
    
    # Additional details
    with st.expander("📄 View Category Details"):
        st.dataframe(cat_info.to_frame(), use_container_width=True)
    
    # Quick links
    st.divider()
    st.subheader("🔗 Quick Navigation")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📋 Browse Rules", use_container_width=True):
            st.session_state['current_view'] = 'rule_list'
            st.rerun()
    
    with col2:
        if st.button("🎯 View by Field", use_container_width=True):
            st.session_state['current_view'] = 'field_view'
            st.rerun()
    
    with col3:
        if st.button("🔗 Dependencies", use_container_width=True):
            st.session_state['current_view'] = 'dependency_graph'
            st.rerun()
