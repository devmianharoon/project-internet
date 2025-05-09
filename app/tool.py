import mysql.connector
from typing import List, Dict
from agents import function_tool

# @function_tool
# def get_providers(provider_names: List[str]) -> List[Dict[str, str]]:
#     """
#     Retrieves provider details (ProviderName, logo, contact) from the internet_companies table
#     for a given list of provider names.

#     Args:
#         provider_names (List[str]): A list of provider names to query (e.g., ["AT&T", "Xfinity"]).

#     Returns:
#         List[Dict[str, str]]: A list of dictionaries containing ProviderName, logo, and contact
#         for each matching provider. Returns an empty list if no matches are found.

#     Raises:
#         mysql.connector.Error: If a database connection or query error occurs.
#         Exception: For other unexpected errors.
#     """
#     # Database configuration
#     db_config = {
#         "host": "localhost",
#         "user": "nearme_us",
#         "password": "nearme&j417Btt5",
#         "database": "internet_nrearme"
#     }

#     try:
#         # Connect to the database
#         conn = mysql.connector.connect(**db_config)
#         cursor = conn.cursor(dictionary=True)

#         # Create a parameterized query to prevent SQL injection
#         placeholders = ",".join(["%s"] * len(provider_names))
#         query = f"SELECT ProviderName, logo, contact FROM internet_companies WHERE ProviderName IN ({placeholders})"
        
#         # Execute the query with the list of provider names
#         cursor.execute(query, provider_names)
#         providers = cursor.fetchall()

#         # Close the cursor and connection
#         cursor.close()
#         conn.close()
#         # print(providers)

#         return providers

#     except mysql.connector.Error as e:
#         print(f"Database error: {str(e)}")
#         raise
#     except Exception as e:
#         print(f"Error: {str(e)}")
#         raise

@function_tool
def get_providers(provider_names: List[str]) -> List[Dict[str, str]]:
    # print(provider_names)
    """
    Retrieves provider details (ProviderName, logo, contact) from the internet_companies table
    for a given list of provider names. Returns an empty dictionary for providers not found.

    Args:
        provider_names (List[str]): A list of provider names to query (e.g., ["AT&T", "Xfinity"]).

    Returns:
        List[Dict[str, str]]: A list of dictionaries containing ProviderName, logo, and contact
        for each matching provider. For providers not found, an empty dictionary is included.

    Raises:
        mysql.connector.Error: If a database connection or query error occurs.
    """
    # Database configuration
    db_config = {
        "host": "localhost",
        "user": "nearme_us",
        "password": "nearme&j417Btt5",
        "database": "internet_nrearme"
    }

    # Initialize the result list
    result = []

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

        # Create a set of provider names found in the database
        found_providers = {provider["ProviderName"] for provider in providers}

        # Add found providers to the result
        result.extend(providers)

        # Add empty dictionaries for providers not found
        for provider_name in provider_names:
            if provider_name not in found_providers:
                result.append({"ProviderName": provider_name, "logo": "", "contact": ""})

        # Close the cursor and connection
        cursor.close()
        conn.close()
        # print(providers)

        return result

    except mysql.connector.Error as e:
        print(f"Database error: {str(e)}")
        raise