"""
Transforms and Loads data into the Databricks database

"""

import os
from databricks import sql
import pandas as pd
from dotenv import load_dotenv


def load(
    dataset="/Users/tusunaiturumbekova/SQL_Query_Databricks1_Tursunai/data/urbanization.csv",
):
    """Transforms and Loads the top 5 locations by urbanindex for each state into the Databricks database."""
    # Load the dataset into a DataFrame
    df = pd.read_csv(dataset, delimiter=",")

    # Transform: Select top 5 locations by urbanindex for each state
    df_top5 = df.sort_values(by=["state", "urbanindex"], ascending=[True, False])
    df_top5 = df_top5.groupby("state").head(5).reset_index(drop=True)

    # Load environment variables
    load_dotenv()
    server_host = os.getenv("SERVER_HOSTNAME")
    access_token = os.getenv("ACCESS_TOKEN")
    http_path = os.getenv("HTTP_PATH")

    # Connect to Databricks and create the table
    try:
        with sql.connect(
            server_hostname=server_host,
            http_path=http_path,
            access_token=access_token,
        ) as connection:
            c = connection.cursor()

            # Drop the existing table and create a new one
            c.execute("DROP TABLE IF EXISTS default.urbanizationDB")
            c.execute(
                "CREATE TABLE default.urbanizationDB (statefips INT, state STRING, gisjoin STRING, lat_tract FLOAT, long_tract FLOAT, population INT, adj_radiuspop_5 FLOAT, urbanindex FLOAT)"
            )

            # Prepare the transformed data for insertion
            data_to_insert = df_top5.values.tolist()
            insert_query = """
                INSERT INTO default.urbanizationDB (statefips, state, gisjoin, lat_tract, long_tract, population, adj_radiuspop_5, urbanindex)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """

            # Execute the data insertion
            c.executemany(insert_query, data_to_insert)
            connection.commit()  # Commit the changes
            c.close()

        print("Data inserted successfully.")
        return "success"

    except Exception as e:
        print(f"An error occurred: {e}")
        return "failure"


if __name__ == "__main__":
    load()
