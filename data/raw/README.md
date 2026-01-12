# Data Directory

Place your CSV extracts from SAP SE16 here.

## Required Files

Files can be either CSV or XLSX format:

- `zpd_prd_categ.csv` (or .xlsx)
- `zpd_script_dtl.csv` (or .xlsx)
- `zpd_script_con.csv` (or .xlsx)
- `zpd_slrule_def.csv` (or .xlsx)

## Optional Files

- `zpd_slrule_val.csv` (or .xlsx)
- `zpd_slrule_opt.csv` (or .xlsx)
- `zpd_shar_rule.csv` (or .xlsx)
- `zpd_function_rule.csv` (or .xlsx)

## SE16 Export Instructions

1. Run transaction **SE16** or **SE16N**
2. Enter table name (e.g., `ZPD_SCRIPT_DTL`)
3. Set filters:
   - PROD_CATEG = 'MM_EXTEND' (or your category)
   - PROD_CATEG_TYPE = (your type)
   - DATA_SET = (your dataset)
   - VERSION = (your version)
4. Execute
5. Export to file (Menu: List > Export > Spreadsheet)
6. Save as CSV or XLSX with exact filename listed above
7. Place in this directory

## Notes

- Filenames must be lowercase
- Use `.csv` or `.xlsx` extension
- Ensure files have headers (column names)
- Empty files are okay for optional tables
- App will automatically detect CSV or Excel format
