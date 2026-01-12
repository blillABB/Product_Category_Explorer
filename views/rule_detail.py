"""
Rule Detail View
Deep dive into a single rule
"""
import streamlit as st
import pandas as pd
from typing import Dict
from utils.joins import get_rule_details

def render_rule_detail(tables: Dict[str, pd.DataFrame], rule_id: str):
    """Render detailed view of a single rule"""
    
    details = get_rule_details(tables, rule_id)
    
    if details is None:
        st.error(f"Rule {rule_id} not found")
        return
    
    header = details['header']
    
    # Back button
    if st.button("⬅️ Back to Rule List"):
        st.session_state['current_view'] = 'rule_list'
        st.rerun()
    
    st.divider()
    
    # Header
    st.title(f"🔍 Rule Detail: {header['Rule']}")

    # Parse RULE_TYPE from Rule column (first 2 chars of rule ID)
    header['RULE_TYPE'] = header['Rule'][:2]

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Sequence", header['Processing Sequence'])
    with col2:
        type_labels = {'01': 'Selection', '02': 'Sub-Process', '03': 'Function', '04': 'Classification'}
        st.metric("Type", type_labels.get(header['RULE_TYPE'], header['RULE_TYPE']))
    with col3:
        st.metric("Rule ID", header['Rule'])

    st.subheader(header['Dsgn Bldr Scrpt Prcs'])
    if header.get('RULE_DESC'):
        st.caption(header['RULE_DESC'])

    st.divider()

    # Rule-type specific rendering
    if header['RULE_TYPE'] == '01':
        render_selection_rule(details)
    elif header['RULE_TYPE'] == '02':
        render_subprocess_rule(details)
    elif header['RULE_TYPE'] == '03':
        render_function_rule(details)
    elif header['RULE_TYPE'] == '04':
        render_classification_rule(details)


def render_selection_rule(details: Dict):
    """Render Type 01 - Selection Rule details"""
    
    # Input Variables
    st.subheader("📥 Input Variables")
    if details['inputs']:
        inputs_df = pd.DataFrame(details['inputs'])
        inputs_df = inputs_df[['No.', 'Char. Name', 'Checkbox.2', 'Checkbox.1']].sort_values('No.')
        inputs_df.columns = ['Seq', 'Variable', 'Multiples', 'Range']
        st.dataframe(inputs_df, use_container_width=True, hide_index=True)
    else:
        st.info("No input variables defined")
    
    # Conditions
    st.subheader("⚙️ Conditions")
    if details['conditions']:
        conditions_df = pd.DataFrame(details['conditions'])

        # Group by row
        for row_key in sorted(conditions_df['Row'].unique()):
            row_conds = conditions_df[conditions_df['Row'] == row_key]

            with st.expander(f"Row {row_key}", expanded=(row_key == '0001' or row_key == 1)):
                condition_text = []
                for _, cond in row_conds.iterrows():
                    var = cond['Char. Name']
                    op = cond['Op']

                    # Get value
                    if pd.notna(cond.get('Characteristic Value')):
                        val = cond['Characteristic Value']
                    elif pd.notna(cond.get('Charactristic Numeric Value')):
                        if pd.notna(cond.get('Charactristic Numeric Value.1')):
                            val = f"{cond['Charactristic Numeric Value']} to {cond['Charactristic Numeric Value.1']}"
                        else:
                            val = cond['Charactristic Numeric Value']
                    else:
                        val = "(empty)"

                    connector = cond.get('CONNECTOR', '')

                    condition_text.append(f"**{var}** {op} `{val}` {connector}")

                st.markdown(" ".join(condition_text))
    else:
        st.info("No conditions defined")
    
    # Output Variables & Values
    st.subheader("📤 Output Variables & Values")
    if details['outputs']:
        outputs_df = pd.DataFrame(details['outputs'])

        for _, output in outputs_df.iterrows():
            field_name = output['Char. Name']

            with st.expander(f"🎯 {field_name}", expanded=True):
                # Get values for this output
                if details['values']:
                    values_df = pd.DataFrame(details['values'])
                    field_values = values_df[values_df['Char. Name'] == field_name]

                    if len(field_values) > 0:
                        for row_key in sorted(field_values['Row'].unique()):
                            row_vals = field_values[field_values['Row'] == row_key]

                            for _, val in row_vals.iterrows():
                                if pd.notna(val.get('Characteristic Value')):
                                    value_display = val['Characteristic Value']
                                elif pd.notna(val.get('Val from')):
                                    value_display = val['Val from']
                                else:
                                    value_display = "(empty)"

                                if row_key == '0000' or row_key == 0:
                                    st.markdown(f"**Default:** `{value_display}`")
                                else:
                                    st.markdown(f"**Row {row_key}:** `{value_display}`")
                    else:
                        st.info("No values defined")
                else:
                    st.info("No values defined")
    else:
        st.info("No output variables defined")
    
    # Transactions
    if details['transactions']:
        st.subheader("💼 Transactions")
        trans_df = pd.DataFrame(details['transactions'])

        for row_key in sorted(trans_df['Row'].unique()):
            row_trans = trans_df[trans_df['Row'] == row_key]

            with st.expander(f"Row {row_key} Transactions ({len(row_trans)} items)"):
                display_trans = row_trans[[
                    'ACTION_CODE', 'OBJECT_TYP', 'OBJECT_KEY', 'OBJ_DATA', 'COMP_QTY', 'COMP_UNIT'
                ]].copy()
                display_trans.columns = ['Action', 'Type', 'Key', 'Data', 'Qty', 'Unit']
                st.dataframe(display_trans, use_container_width=True, hide_index=True)


def render_subprocess_rule(details: Dict):
    """Render Type 02 - Sub-Process Rule details"""
    
    st.subheader("🔗 Sub-Processes Called")
    
    if details['subprocesses']:
        subproc_df = pd.DataFrame(details['subprocesses'])

        for _, subproc in subproc_df.iterrows():
            st.info(f"📦 Calls: **{subproc['PrdCat']}** ({subproc['Cat Type']})")
            if subproc.get('Dsgn Bldr Scrpt Prcs'):
                st.caption(f"Process: {subproc['Dsgn Bldr Scrpt Prcs']}")
    else:
        st.warning("No sub-processes defined")


def render_function_rule(details: Dict):
    """Render Type 03 - Function Call Rule details"""
    
    st.subheader("⚙️ Function Call")
    st.info("🔧 Logic is in custom ABAP function module")
    st.caption("To view implementation, check the function module code in SE37")
    
    # If we had function rule table, we'd show it here
    st.markdown("""
    **Note:** Function rules execute custom ABAP code that can:
    - Read and modify NVP variables
    - Perform complex calculations
    - Add/modify transactions
    - Generate messages
    """)


def render_classification_rule(details: Dict):
    """Render Type 04 - Classification Search Rule details"""
    
    st.subheader("🔍 Classification Search")
    st.info("🏷️ Searches SAP classification system")
    st.caption("Results depend on classification catalog configuration")
    
    st.markdown("""
    **Note:** Classification rules:
    - Search for materials/equipment in SAP class system
    - Match based on characteristics
    - Return found objects as transactions
    - Set variables from classification data
    """)
