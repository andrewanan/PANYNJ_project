import pandas as pd
from tabulate import tabulate

file_path = 'C:/Users/aanantharajah/Downloads/internProject/TRN-201 Transaction Research.csv'

dtype_spec = {
    'Plaza': str,
    'Resl': str,
    # Add other column specifications as needed
}

df = pd.read_csv(file_path, skiprows=8, on_bad_lines='skip', dtype=dtype_spec, low_memory=False)

df['Trx Tmst'] = pd.to_datetime(df['Trx Tmst'], errors='coerce')
df['HalfHour'] = df['Trx Tmst'].dt.floor('30T')

df['Plaza'].fillna('Unknown', inplace=True)
df['Resl'].fillna('Unknown', inplace=True)

# Create a simplified DataFrame
df_simplified = df[['Plaza', 'Resl', 'Trx Tmst']].copy()

# Check the simplified DataFrame
print(df_simplified.info())

# Verify the contents
print(df_simplified.head())

# Attempt to create the pivot table
reverse_flush = df_simplified.pivot_table(index='Plaza', columns='Resl', values='Plaza', aggfunc='count', fill_value=0)

print("\nReverse Flush\n")
print(tabulate(reverse_flush, headers='keys', tablefmt='github'))
