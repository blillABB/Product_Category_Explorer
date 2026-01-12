"""
Field-Centric View
See all rules that set a specific field
"""
import streamlit as st
import pandas as pd
from typing import Dict
from utils.joins import get_fields_set, get_rules_for_field

def render_field_view(tables: Dict[str, pd.DataFrame]):
    """Render the field-centric view"""
    
    st.title("🎯 Field-Centric View")
    
    # Get list of all fields
    fields_df = get_fields_set(tables)
    
    if len(fields_df) == 0:
        st.warning("No output fields found")
        return
    
    # Layout: sidebar for field list, main area for details
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.subheader("📋 Output Fields")
        
        # Search
        search = st.text_input("Search fields", key="field_search")
        
        # Filter fields
        filtered_fields = fields_df.copy()
        if search:
            filtered_fields = filtered_fields[
                filtered_fields['Char. Name'].str.contains(search, case=False, na=False)
            ]

        # Sort options
        sort_by = st.radio(
            "Sort by",
            ["Name", "# Rules"],
            key="field_sort"
        )

        if sort_by == "Name":
            filtered_fields = filtered_fields.sort_values('Char. Name')
        else:
            filtered_fields = filtered_fields.sort_values('rule_count', ascending=False)

        st.info(f"📊 {len(filtered_fields)} fields")

        # Display field list as radio buttons
        if len(filtered_fields) > 0:
            selected_field = st.radio(
                "Select field:",
                filtered_fields['Char. Name'].tolist(),
                format_func=lambda x: f"{x} ({filtered_fields[filtered_fields['Char. Name']==x].iloc[0]['rule_count']})",
                key="selected_field",
                label_visibility="collapsed"
            )
        else:
            selected_field = None
    
    with col2:
        if selected_field:
            render_field_details(tables, selected_field)
        else:
            st.info("👈 Select a field from the list to view details")


def render_field_details(tables: Dict[str, pd.DataFrame], field_name: str):
    """Render details for a specific field"""
    
    st.subheader(f"Field: {field_name}")
    
    # Get rules that set this field
    rules_df = get_rules_for_field(tables, field_name)

    if len(rules_df) == 0:
        st.warning("No rules found for this field")
        return

    # Parse RULE_TYPE from Rule column (first 2 chars of rule ID)
    rules_df['RULE_TYPE'] = rules_df['Rule'].str[:2]

    # Summary metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Rules Setting Field", len(rules_df))

    with col2:
        seq_min = rules_df['Processing Sequence'].min()
        seq_max = rules_df['Processing Sequence'].max()
        st.metric("Sequence Range", f"{seq_min} - {seq_max}")

    with col3:
        rule_types = rules_df['RULE_TYPE'].nunique()
        st.metric("Rule Types", rule_types)
    
    st.divider()
    
    # Show each rule
    st.subheader("📋 Rules")
    
    for idx, (_, rule) in enumerate(rules_df.iterrows(), 1):
        with st.expander(
            f"#{idx}: {rule['Rule']} - {rule['Dsgn Bldr Scrpt Prcs']} (Seq {rule['Processing Sequence']})",
            expanded=(idx == 1)
        ):
            col1, col2 = st.columns([1, 3])

            with col1:
                type_labels = {
                    '01': 'Selection',
                    '02': 'Sub-Process',
                    '03': 'Function',
                    '04': 'Classification'
                }
                st.markdown(f"**Type:** {type_labels.get(rule['RULE_TYPE'], rule['RULE_TYPE'])}")
                st.markdown(f"**Sequence:** {rule['Processing Sequence']}")
                st.markdown(f"**Rule ID:** `{rule['Rule']}`")

            with col2:
                if rule.get('RULE_DESC'):
                    st.markdown(f"**Description:** {rule['RULE_DESC']}")

                # Show values set (if available)
                if 'values_set' in rule.index and pd.notna(rule['values_set']):
                    st.markdown("**Values Set:**")
                    for value_line in rule['values_set'].split(', '):
                        st.markdown(f"- {value_line}")

                # View details button
                if st.button(f"View Full Rule Details", key=f"view_{rule['Rule']}"):
                    st.session_state['current_view'] = 'rule_detail'
                    st.session_state['selected_rule'] = rule['Rule']
                    st.rerun()
    
    # Potential conflicts warning
    if len(rules_df) > 1:
        st.divider()
        st.warning(f"""
        ⚠️ **Multiple Rules Set This Field**
        
        This field is set by {len(rules_df)} different rules. Depending on conditions:
        - Multiple rules might fire in the same execution
        - The last rule to execute (highest sequence) will determine final value
        - This can make debugging difficult
        
        **Consider refactoring** to consolidate all logic for this field into a single module.
        """)
