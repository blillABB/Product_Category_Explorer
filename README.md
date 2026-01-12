# Product Category Browser

A Streamlit web application for browsing and analyzing SAP Decision Engine product categories.

## Features

- **Category Overview**: High-level statistics and rule breakdown
- **Rule List**: Browse all rules with filtering and search
- **Rule Detail**: Deep dive into individual rules (conditions, outputs, transactions)
- **Field-Centric View**: See all rules that set a specific field
- **Dependency Graph**: Visualize field dependencies

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Prepare Data

Extract the following tables from SAP using SE16 and save as CSV or XLSX files in `/data/raw/`:

**Required:**
- `zpd_prd_categ.csv` (or .xlsx) - Category master
- `zpd_script_dtl.csv` (or .xlsx) - Rule definitions
- `zpd_script_con.csv` (or .xlsx) - Rule conditions
- `zpd_slrule_def.csv` (or .xlsx) - Selection rule I/O definitions

**Optional (but recommended):**
- `zpd_slrule_val.csv` (or .xlsx) - Selection rule output values
- `zpd_slrule_opt.csv` (or .xlsx) - Selection rule transactions
- `zpd_shar_rule.csv` (or .xlsx) - Sub-process links

**SE16 Filter Criteria:**

For category MM_EXTEND:
```
PROD_CATEG = 'MM_EXTEND'
PROD_CATEG_TYPE = [your type]
DATA_SET = [your dataset]
VERSION = [your version]
```

For tables that don't have PROD_CATEG directly (like zpd_slrule_*):
1. First extract zpd_script_dtl to get list of RULE_IDs
2. Then filter by those RULE_IDs

### 3. File Structure

```
product_category_browser/
├── app.py                      # Main app
├── requirements.txt
├── data/
│   └── raw/                    # Put CSV files here
│       ├── zpd_prd_categ.csv
│       ├── zpd_script_dtl.csv
│       ├── zpd_script_con.csv
│       └── ...
├── views/                      # View modules
│   ├── overview.py
│   ├── rule_list.py
│   ├── rule_detail.py
│   ├── field_view.py
│   └── dependency_graph.py
└── utils/                      # Utilities
    ├── data_loader.py
    └── joins.py
```

## Usage

### Start the App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

### Navigation

Use the sidebar to navigate between views:

1. **Overview** - Start here to see category statistics
2. **Rule List** - Browse and search all rules
3. **Field View** - Analyze which rules set specific fields
4. **Dependencies** - Understand field relationships

### Typical Workflows

**Understanding a Rule:**
1. Go to Rule List
2. Filter/search to find your rule
3. Click "View Rule Details"

**Finding Logic for a Field:**
1. Go to Field View
2. Select field from left panel
3. See all rules that set it

**Planning Refactoring:**
1. Go to Field View
2. Look for fields set by multiple rules (warning will appear)
3. Use Dependencies view to understand execution order

## Data Notes

### Rule Types

- **Type 01**: Selection rules (most common)
- **Type 02**: Sub-process calls
- **Type 03**: Function module calls
- **Type 04**: Classification searches

### Missing Data

If `zpd_slrule_val.csv` has no records, it means:
- Category may use functions (Type 03) instead of selection rules
- Or output values may be stored differently
- The app will still work, just won't show detailed values

## Troubleshooting

### "Missing Required Data Files" Error

- Ensure all CSV files are in `/data/raw/` directory
- Check that filenames exactly match (lowercase, with .csv extension)
- Verify files contain data (not empty)

### "No rules found" Warning

- Check PROD_CATEG filter in your SE16 extract
- Verify you extracted the correct dataset/version

### Performance Issues

- If you have >500 rules, initial load may be slow
- Data is cached after first load
- Use filters to reduce displayed data

## Future Enhancements

- [ ] Export functionality (filtered results to CSV/Excel)
- [ ] Visual flow diagram (execution sequence)
- [ ] Interactive dependency graph (network visualization)
- [ ] Compare two categories side-by-side
- [ ] Rule validation (detect conflicts, missing conditions)
- [ ] Support for Type 03/04 rule details
- [ ] Edit capability (generate new rules)

## Support

For issues or questions, contact the development team.
