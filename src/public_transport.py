import requests
import pandas as pd


def fetch_gps_data(url: str) -> list[dict]:
    """
    Fetch GPS data from an external API.
    This is a placeholder function; replace with actual API call.
    """
    # Request the data from the API
    response = requests.get(url)

    # Get content from the response
    data = response.text

    # split the data into rows and columns
    rows = [x.split(",") for x in data.split("\n") if x.strip()]

    # Create a DataFrame from the rows
    df = pd.DataFrame(rows)

    # Assuming the first row contains headers
    df.columns = df.iloc[0]  # Set the first row as column headers

    # Drop the first row as it is now the header
    df = df[1:]

    # Reset index (optional)
    df = df.reset_index(drop=True)

    # Convert to list of records
    records = df.to_dict(orient="records")  # Convert DataFrame to list of records

    return records
