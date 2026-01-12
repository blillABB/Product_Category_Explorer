"""
Dependency Graph View
Visualize field dependencies
"""
import streamlit as st
import pandas as pd
from typing import Dict
from utils.joins import get_field_dependencies

def render_dependency_graph(tables: Dict[str, pd.DataFrame]):
    """Render the dependency graph view"""
    
    st.title("🔗 Field Dependencies")
    
    st.info("📊 This view shows which fields depend on other fields")
    
    # Get dependencies
    deps_df = get_field_dependencies(tables)
    
    if len(deps_df) == 0:
        st.warning("No dependencies found")
        return
    
    # Show as table for now (graph visualization can be added later)
    st.subheader("Dependency Table")
    
    st.markdown("""
    This table shows field relationships:
    - **Output Field**: The field being set
    - **Input Field**: The field it depends on (reads)
    - **Rule Count**: Number of rules with this dependency
    """)
    
    # Format for display
    display_df = deps_df.copy()
    display_df.columns = ['Output Field', 'Input Field', 'Rule Count']
    
    st.dataframe(display_df, use_container_width=True, hide_index=True, height=600)
    
    st.divider()
    
    # Execution order implications
    st.subheader("💡 Execution Order Implications")
    
    st.markdown("""
    **For field-centric refactoring, consider this dependency order:**
    
    1. **Independent fields** (no dependencies) should be set first
    2. **Intermediate fields** (depend on others, are used by others) in the middle
    3. **Final fields** (depend on others, not used by others) last
    """)
    
    # Find fields with no dependencies (candidates to run first)
    all_outputs = set(deps_df['output_field'].unique())
    all_inputs = set(deps_df['input_field'].unique())
    
    independent = all_outputs - all_inputs
    final_outputs = all_outputs - set(deps_df['input_field'].unique())
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🟢 Independent Fields** (no dependencies)")
        if independent:
            for field in sorted(independent):
                st.markdown(f"- `{field}`")
        else:
            st.info("None found")
    
    with col2:
        st.markdown("**🔴 Final Output Fields** (not used by others)")
        if final_outputs:
            for field in sorted(final_outputs):
                st.markdown(f"- `{field}`")
        else:
            st.info("None found")
