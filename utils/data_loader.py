"""
Data loading utilities for Product Category Browser
Handles loading and caching of SAP table extracts
"""
import pandas as pd
import streamlit as st
from pathlib import Path
from typing import Dict, Optional

DATA_DIR = Path(__file__).parent.parent / "data" / "raw"

# Define expected files and their key columns (using actual XLSX column names)
TABLE_SCHEMAS = {
    'zpd_prd_categ': ['PrdCat', 'Cat Type', 'DS'],
    'zpd_script_dtl': ['Rule', 'Processing Sequence', 'Dsgn Bldr Scrpt Prcs', 'PrdCat', 'DS', 'Ver. No.'],
    'zpd_script_con': ['Rule', 'Char. Name', 'Op', 'Row'],
    'zpd_slrule_def': ['Rule', 'Char. Name', 'Character Length 1', 'No.'],
    'zpd_slrule_val': ['Rule', 'Row', 'Char. Name', 'Characteristic Value', 'Val from'],
    'zpd_slrule_opt': ['Rule', 'Row', 'ACTION_CODE', 'OBJECT_TYP', 'OBJ_DATA'],
    'zpd_shar_rule': ['Rule', 'PrdCat', 'Cat Type', 'Dsgn Bldr Scrpt Prcs'],
}

OPTIONAL_TABLES = ['zpd_function_rule', 'zpd_shar_rule', 'zpd_slrule_opt', 'zpd_slrule_val']

@st.cache_data
def load_table(table_name: str) -> Optional[pd.DataFrame]:
    """
    Load a single CSV or XLSX file into a DataFrame
    
    Args:
        table_name: Name of the table (without extension)
        
    Returns:
        DataFrame if file exists and is valid, None otherwise
    """
    # Try CSV first, then XLSX
    csv_path = DATA_DIR / f"{table_name}.csv"
    xlsx_path = DATA_DIR / f"{table_name}.xlsx"
    
    file_path = None
    if csv_path.exists():
        file_path = csv_path
    elif xlsx_path.exists():
        file_path = xlsx_path
    else:
        if table_name in OPTIONAL_TABLES:
            return None
        else:
            st.error(f"❌ Required file not found: {table_name}.csv or {table_name}.xlsx")
            return None
    
    try:
        # Read based on file type
        if file_path.suffix == '.csv':
            df = pd.read_csv(file_path)
        else:  # .xlsx
            df = pd.read_excel(file_path)
        
        # Validate expected columns exist
        expected_cols = TABLE_SCHEMAS.get(table_name, [])
        missing_cols = [col for col in expected_cols if col not in df.columns]
        
        if missing_cols:
            st.warning(f"⚠️ {table_name} is missing columns: {missing_cols}")
        
        return df
    
    except Exception as e:
        st.error(f"❌ Error loading {table_name}: {str(e)}")
        return None


@st.cache_data
def load_all_tables() -> Dict[str, pd.DataFrame]:
    """
    Load all required CSV files
    
    Returns:
        Dictionary mapping table names to DataFrames
    """
    tables = {}
    
    for table_name in TABLE_SCHEMAS.keys():
        df = load_table(table_name)
        if df is not None:
            tables[table_name] = df
    
    return tables


def get_category_info(tables: Dict[str, pd.DataFrame], 
                     prod_categ: str = None) -> Optional[pd.Series]:
    """
    Get category master record
    
    Args:
        tables: Dictionary of loaded tables
        prod_categ: Product category to filter (if None, returns first record)
        
    Returns:
        Series with category info, or None if not found
    """
    if 'zpd_prd_categ' not in tables:
        return None
    
    df = tables['zpd_prd_categ']

    if prod_categ:
        filtered = df[df['PrdCat'] == prod_categ]
        if len(filtered) == 0:
            return None
        return filtered.iloc[0]
    else:
        # Return first record if no filter
        return df.iloc[0] if len(df) > 0 else None


def validate_data_loaded(tables: Dict[str, pd.DataFrame]) -> tuple[bool, list[str]]:
    """
    Validate that required tables are loaded
    
    Args:
        tables: Dictionary of loaded tables
        
    Returns:
        Tuple of (is_valid, list of missing tables)
    """
    required_tables = [t for t in TABLE_SCHEMAS.keys() if t not in OPTIONAL_TABLES]
    missing = [t for t in required_tables if t not in tables or tables[t] is None]
    
    return len(missing) == 0, missing
