"""
Data Aggregator
Group and aggregate data with multiple statistics
"""
import pandas as pd
import numpy as np
import argparse
import json
from typing import Dict, List


class DataAggregator:
    """Advanced data aggregation with grouping"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
    
    def aggregate(self, group_by: List[str], 
                  agg_columns: Dict[str, List[str]]) -> pd.DataFrame:
        """
        Aggregate data by groups
        
        Args:
            group_by: Columns to group by
            agg_columns: Dict of {column: [aggregation functions]}
                        e.g., {'sales': ['sum', 'mean', 'count']}
        """
        print(f"📊 Grouping by: {group_by}")
        print(f"📈 Aggregating: {agg_columns}")
        
        # Build aggregation dict
        agg_dict = {}
        for col, funcs in agg_columns.items():
            if len(funcs) == 1:
                agg_dict[col] = funcs[0]
            else:
                agg_dict[col] = funcs
        
        result = self.df.groupby(group_by).agg(agg_dict).reset_index()
        
        # Flatten column names if multi-level
        if isinstance(result.columns, pd.MultiIndex):
            result.columns = [' '.join(col).strip() if col[1] not in ['nan', 'NaN'] else col[0] 
                            for col in result.columns.values]
        
        return result
    
    def pivot_summary(self, index: str, columns: str, values: str, 
                      aggfunc: str = 'sum') -> pd.DataFrame:
        """Create pivot table summary"""
        return pd.pivot_table(
            self.df,
            index=index,
            columns=columns,
            values=values,
            aggfunc=aggfunc,
            fill_value=0
        )
    
    def time_series_aggregate(self, date_column: str, freq: str = 'M') -> pd.DataFrame:
        """
        Aggregate time series data
        
        freq: 'D' daily, 'W' weekly, 'M' monthly, 'Q' quarterly, 'Y' yearly
        """
        # Ensure datetime
        self.df[date_column] = pd.to_datetime(self.df[date_column])
        
        # Set index and resample
        df_time = self.df.set_index(date_column)
        
        # Numeric columns only
        numeric_cols = df_time.select_dtypes(include=[np.number]).columns
        
        return df_time[numeric_cols].resample(freq).agg(['sum', 'mean', 'count'])
    
    def top_n(self, group_by: str, value_col: str, n: int = 5) -> pd.DataFrame:
        """Get top N records per group"""
        return self.df.groupby(group_by).apply(
            lambda x: x.nlargest(n, value_col)
        ).reset_index(drop=True)


def main():
    parser = argparse.ArgumentParser(description='Data Aggregator')
    parser.add_argument('--input', required=True, help='Input CSV file')
    parser.add_argument('--group-by', nargs='+', required=True, 
                       help='Columns to group by')
    parser.add_argument('--agg', required=True,
                       help='Aggregation config (JSON string)')
    parser.add_argument('--output', required=True, help='Output file')
    
    args = parser.parse_args()
    
    # Load data
    print(f"📂 Loading {args.input}...")
    df = pd.read_csv(args.input)
    print(f"   Rows: {len(df):,}")
    
    # Parse aggregation config
    agg_config = json.loads(args.agg)
    
    # Aggregate
    print("\n🔄 Aggregating...")
    aggregator = DataAggregator(df)
    result = aggregator.aggregate(args.group_by, agg_config)
    
    print(f"\n✅ Result: {len(result):,} groups")
    print(result.head())
    
    # Save
    print(f"\n💾 Saving to {args.output}...")
    if args.output.endswith('.json'):
        result.to_json(args.output, orient='records', indent=2)
    elif args.output.endswith('.xlsx'):
        result.to_excel(args.output, index=False)
    else:
        result.to_csv(args.output, index=False)
    
    print("✅ Done!")


if __name__ == '__main__':
    main()
