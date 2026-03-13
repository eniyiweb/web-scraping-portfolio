"""
Data Merger
Merge multiple datasets with different join strategies
"""
import pandas as pd
import argparse
from pathlib import Path
from typing import List, Optional


class DataMerger:
    """Merge multiple datasets with validation"""
    
    def __init__(self):
        self.dataframes = []
    
    def load_files(self, files: List[str]) -> 'DataMerger':
        """Load multiple CSV/JSON files"""
        for file in files:
            print(f"📂 Loading {file}...")
            
            if file.endswith('.json'):
                df = pd.read_json(file)
            else:
                df = pd.read_csv(file)
            
            df['_source_file'] = Path(file).name
            self.dataframes.append(df)
            print(f"   Rows: {len(df):,}, Columns: {len(df.columns)}")
        
        return self
    
    def merge(self, on: Optional[List[str]] = None, 
              how: str = 'inner',
              validate: str = 'one_to_many') -> pd.DataFrame:
        """
        Merge all loaded dataframes
        
        Args:
            on: Columns to join on
            how: 'inner', 'outer', 'left', 'right'
            validate: 'one_to_one', 'one_to_many', 'many_to_one', 'many_to_many'
        """
        if not self.dataframes:
            raise ValueError("No dataframes loaded")
        
        if len(self.dataframes) == 1:
            return self.dataframes[0]
        
        result = self.dataframes[0]
        
        for i, df in enumerate(self.dataframes[1:], 2):
            print(f"\n🔄 Merging dataset {i}...")
            
            if on:
                # Check columns exist
                missing_left = set(on) - set(result.columns)
                missing_right = set(on) - set(df.columns)
                
                if missing_left:
                    raise ValueError(f"Columns not in left: {missing_left}")
                if missing_right:
                    raise ValueError(f"Columns not in right: {missing_right}")
                
                result = pd.merge(
                    result, df,
                    on=on,
                    how=how,
                    suffixes=('', f'_{i}'),
                    validate=validate
                )
            else:
                # Merge on index
                result = result.join(df, rsuffix=f'_{i}')
            
            print(f"   Result: {len(result):,} rows, {len(result.columns)} columns")
        
        return result
    
    def concatenate(self, axis: int = 0, ignore_index: bool = True) -> pd.DataFrame:
        """Concatenate all dataframes vertically (axis=0) or horizontally (axis=1)"""
        print(f"\n📦 Concatenating {len(self.dataframes)} dataframes...")
        
        result = pd.concat(self.dataframes, axis=axis, ignore_index=ignore_index)
        print(f"   Result: {len(result):,} rows, {len(result.columns)} columns")
        
        return result


def main():
    parser = argparse.ArgumentParser(description='Data Merger')
    parser.add_argument('--files', nargs='+', required=True, help='Input files')
    parser.add_argument('--keys', nargs='+', help='Join key columns')
    parser.add_argument('--how', default='inner', 
                       choices=['inner', 'outer', 'left', 'right'],
                       help='Join type')
    parser.add_argument('--mode', default='merge', 
                       choices=['merge', 'concat'],
                       help='Merge mode')
    parser.add_argument('--output', required=True, help='Output file')
    
    args = parser.parse_args()
    
    # Load and merge
    merger = DataMerger().load_files(args.files)
    
    if args.mode == 'merge':
        result = merger.merge(on=args.keys, how=args.how)
    else:
        result = merger.concatenate()
    
    # Save
    print(f"\n💾 Saving to {args.output}...")
    if args.output.endswith('.json'):
        result.to_json(args.output, orient='records', indent=2)
    elif args.output.endswith('.xlsx'):
        result.to_excel(args.output, index=False)
    else:
        result.to_csv(args.output, index=False)
    
    print(f"✅ Done! {len(result):,} rows written")


if __name__ == '__main__':
    main()
