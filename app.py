"""
Product Category Browser
Main Streamlit application
"""
import streamlit as st
from utils.data_loader import load_all_tables, validate_data_loaded
from views import overview, rule_list, rule_detail, field_view, dependency_graph

# Page config
st.set_page_config(
    page_title="Product Category Browser",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
    .stExpander {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main application entry point"""
    
    # Initialize session state
    if 'current_view' not in st.session_state:
        st.session_state['current_view'] = 'overview'
    if 'selected_rule' not in st.session_state:
        st.session_state['selected_rule'] = None
    
    # Load data
    with st.spinner("Loading data..."):
        tables = load_all_tables()
    
    # Validate data
    is_valid, missing = validate_data_loaded(tables)
    
    if not is_valid:
        st.error(f"""
        ❌ **Missing Required Data Files**
        
        The following files are missing from `/data/raw/`:
        {', '.join(missing)}
        
        Please ensure all required CSV exports are in the data directory.
        """)
        st.stop()
    
    # Success message
    st.sidebar.success(f"✅ Loaded {len(tables)} tables")
    
    # Navigation
    st.sidebar.title("📦 Navigation")
    
    view_options = {
        'overview': '📊 Overview',
        'rule_list': '📋 Rule List',
        'field_view': '🎯 Field View',
        'dependency_graph': '🔗 Dependencies'
    }
    
    # Manual navigation buttons
    for view_key, view_label in view_options.items():
        if st.sidebar.button(view_label, use_container_width=True, key=f"nav_{view_key}"):
            st.session_state['current_view'] = view_key
            st.rerun()
    
    st.sidebar.divider()
    
    # Show current location
    current_view = st.session_state['current_view']
    st.sidebar.info(f"📍 Current: {view_options.get(current_view, 'Unknown')}")
    
    # Data info
    with st.sidebar.expander("📊 Data Info"):
        if 'zpd_prd_categ' in tables and len(tables['zpd_prd_categ']) > 0:
            cat_info = tables['zpd_prd_categ'].iloc[0]
            st.markdown(f"**Category:** {cat_info['PrdCat']}")
            st.markdown(f"**Type:** {cat_info['Cat Type']}")
            st.markdown(f"**Dataset:** {cat_info['DS']}")
        
        if 'zpd_script_dtl' in tables:
            st.markdown(f"**Rules:** {len(tables['zpd_script_dtl'])}")
    
    # Render current view
    st.sidebar.divider()
    
    if current_view == 'overview':
        overview.render_overview(tables)
    
    elif current_view == 'rule_list':
        rule_list.render_rule_list(tables)
    
    elif current_view == 'rule_detail':
        if st.session_state['selected_rule']:
            rule_detail.render_rule_detail(tables, st.session_state['selected_rule'])
        else:
            st.warning("No rule selected")
            if st.button("Go to Rule List"):
                st.session_state['current_view'] = 'rule_list'
                st.rerun()
    
    elif current_view == 'field_view':
        field_view.render_field_view(tables)
    
    elif current_view == 'dependency_graph':
        dependency_graph.render_dependency_graph(tables)
    
    else:
        st.error(f"Unknown view: {current_view}")

if __name__ == "__main__":
    main()
