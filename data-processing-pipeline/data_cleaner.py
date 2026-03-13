"""
Data Cleaning Module
Clean and validate datasets with common data quality issues
"""
import pandas as pd
import numpy as np
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json


class DataCleaner:
    """Comprehensive data cleaning toolkit"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.cleaning_log = []
    
    def clean(self, steps: List[str] = None) -> pd.DataFrame:
        """Run cleaning pipeline"""
        steps = steps or ['duplicates', 'nulls', 'whitespace', 'types']
        
        for step in steps:
            if hasattr(self, f'_{step}'):
                getattr(self, f'_{step}')()
        
        return self.df
    
    def _duplicates(self):
        """Remove duplicate rows"""
        before = len(self.df)
        self.df = self.df.drop_duplicates()
        after = len(self.df)
        removed = before - after
        if removed > 0:
            self.cleaning_log.append(f"Removed {removed} duplicate rows")
    
    def _nulls(self):
        """Handle null values"""
        # Log null counts
        null_counts = self.df.isnull().sum()
        null_cols = null_counts[null_counts > 0]
        
        if len(null_cols) > 0:
            self.cleaning_log.append(f"Columns with nulls: {null_cols.to_dict()}")
            
            # Fill numeric columns with median
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                if self.df[col].isnull().any():
                    median = self.df[col].median()
                    self.df[col] = self.df[col].fillna(median)
                    self.cleaning_log.append(f"Filled nulls in '{col}' with median: {median}")
            
            # Fill text columns with 'Unknown'
            text_cols = self.df.select_dtypes(include=['object']).columns
            for col in text_cols:
                if self.df[col].isnull().any():
                    self.df[col] = self.df[col].fillna('Unknown')
                    self.cleaning_log.append(f"Filled nulls in '{col}' with 'Unknown'")
    
    def _whitespace(self):
        """Clean whitespace in text columns"""
        text_cols = self.df.select_dtypes(include=['object']).columns
        
        for col in text_cols:
            if self.df[col].dtype == 'object':
                self.df[col] = self.df[col].str.strip()
        
        self.cleaning_log.append("Trimmed whitespace from text columns")
    
    def _types(self):
        """Optimize data types"""
        # Downcast numeric types
        for col in self.df.select_dtypes(include=[np.number]).columns:
            if self.df[col].dtype == 'float64':
                self.df[col] = pd.to_numeric(self.df[col], downcast='float')
            elif self.df[col].dtype == 'int64':
                self.df[col] = pd.to_numeric(self.df[col], downcast='integer')
        
        # Convert date columns
        for col in self.df.columns:
            if 'date' in col.lower() or 'time' in col.lower():
                try:
                    self.df[col] = pd.to_datetime(self.df[col], errors='ignore')
                    self.cleaning_log.append(f"Converted '{col}' to datetime")
                except:
                    pass
        
        self.cleaning_log.append("Optimized data types")
    
    def standardize_columns(self, column_mapping: Dict[str, str]):
        """Rename columns according to mapping"""
        self.df = self.df.rename(columns=column_mapping)
        self.cleaning_log.append(f"Renamed columns: {column_mapping}")
    
    def validate_email(self, column: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Validate email addresses"""
        import re
        
        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        valid_mask = self.df[column].str.match(email_pattern, na=False)
        
        valid = self.df[valid_mask]
        invalid = self.df[~valid_mask]
        
        self.cleaning_log.append(
            f"Email validation: {len(valid)} valid, {len(invalid)} invalid"
        )
        
        return valid, invalid
    
    def get_report(self) -> Dict:
        """Generate cleaning report"""
        return {
            'rows_final': len(self.df),
            'columns': list(self.df.columns),
            'dtypes': self.df.dtypes.astype(str).to_dict(),
            'null_counts': self.df.isnull().sum().to_dict(),
            'cleaning_log': self.cleaning_log
        }


def main():
    parser = argparse.ArgumentParser(description='Data Cleaner')
    parser.add_argument('--input', required=True, help='Input file (CSV/JSON)')
    parser.add_argument('--output', required=True, help='Output file')
    parser.add_argument('--report', help='Report JSON file')
    
    args = parser.parse_args()
    
    # Load data
    print(f"📂 Loading {args.input}...")
    if args.input.endswith('.json'):
        df = pd.read_json(args.input)
    else:
        df = pd.read_csv(args.input)
    
    print(f"   Rows: {len(df):,}, Columns: {len(df.columns)}")
    
    # Clean
    print("\n🧹 Cleaning data...")
    cleaner = DataCleaner(df)
    cleaned_df = cleaner.clean()
    
    # Save
    print(f"\n💾 Saving to {args.output}...")
    if args.output.endswith('.json'):
        cleaned_df.to_json(args.output, orient='records', indent=2)
    elif args.output.endswith('.xlsx'):
        cleaned_df.to_excel(args.output, index=False)
    else:
        cleaned_df.to_csv(args.output, index=False)
    
    # Report
    report = cleaner.get_report()
    print(f"\n✅ Cleaned! Final rows: {report['rows_final']:,}")
    
    for log in report['cleaning_log']:
        print(f"   • {log}")
    
    if args.report:
        with open(args.report, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        print(f"\n📊 Report saved to {args.report}")


if __name__ == '__main__':
    main()
