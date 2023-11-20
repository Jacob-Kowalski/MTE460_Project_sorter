

import csv

def read_csv(file_path):
    """
    Opens and reads the rows of a CSV file.

    Parameters:
    - file_path (str): The path to the CSV file.

    Returns:
    - list of lists: A list where each element is a list representing a row in the CSV file.
    """
    rows = []

    with open(file_path, 'r') as csvfile:
        # Create a CSV reader object
        csv_reader = csv.reader(csvfile)

        # Read each row and append it to the list
        for row in csv_reader:
            rows.append(row)

    return rows

# Example usage:
csv_file_path = 'path/to/your/file.csv'
csv_rows = read_csv(csv_file_path)

# Print the rows
for row in csv_rows:
    print(row)

# Function to read the next order csv.
def fetch_next_order():
    