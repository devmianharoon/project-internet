import mysql.connector
from typing import List, Dict
from agents import function_tool

@function_tool
def get_providers(provider_names: List[str]) -> List[Dict[str, str]]:
    """
    Retrieves provider details (ProviderName, logo, contact) from the internet_companies table
    for a given list of provider names.

    Args:
        provider_names (List[str]): A list of provider names to query (e.g., ["AT&T", "Xfinity"]).

    Returns:
        List[Dict[str, str]]: A list of dictionaries containing ProviderName, logo, and contact
        for each matching provider. Returns an empty list if no matches are found.

    Raises:
        mysql.connector.Error: If a database connection or query error occurs.
        Exception: For other unexpected errors.
    """
    # Database configuration
    db_config = {
        "host": "localhost",
        "user": "nearme_us",
        "password": "nearme&j417Btt5",
        "database": "internet_nrearme"
    }

    try:
        # Connect to the database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Create a parameterized query to prevent SQL injection
        placeholders = ",".join(["%s"] * len(provider_names))
        query = f"SELECT ProviderName, logo, contact FROM internet_companies WHERE ProviderName IN ({placeholders})"
        
        # Execute the query with the list of provider names
        cursor.execute(query, provider_names)
        providers = cursor.fetchall()

        # Close the cursor and connection
        cursor.close()
        conn.close()

        return providers

    except mysql.connector.Error as e:
        print(f"Database error: {str(e)}")
        raise
    except Exception as e:
        print(f"Error: {str(e)}")
        raise