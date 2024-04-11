import pandas as pd

# Create a sample DataFrame
data = {'Name': ['Alice', 'Bob', 'Charlie'], 'Age': [25, 30, 28]}
df = pd.DataFrame(data)

# Create a dictionary for the new row
new_row = {'Name': 'David', 'Age': 35}

# Append the new row to the DataFrame
df = df.append(new_row, ignore_index=True)

print(df)
