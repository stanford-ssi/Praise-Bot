import os
import pandas as pd
import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host=os.environ['DB_HOST'],
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASS'],
        database=os.environ['DB_DATABASE']
    )

def list_tables(conn):
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    tables = [row[0] for row in cursor.fetchall()]
    cursor.close()
    return tables

def export_table_to_excel(conn, table_name):
    df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
    filename = f"{table_name}.xlsx"
    df.to_excel(filename, index=False)
    print(f"✅ Exported '{table_name}' to {filename}")

def main():
    try:
        conn = get_connection()
        print("✅ Connected to database")

        tables = list_tables(conn)
        if not tables:
            print("❌ No tables found in the database.")
            return

        print("\nAvailable tables:")
        for idx, table in enumerate(tables):
            print(f"[{idx}] {table}")

        selection = input("\nEnter the number of the table to export: ")
        try:
            index = int(selection)
            if 0 <= index < len(tables):
                export_table_to_excel(conn, tables[index])
            else:
                print("❌ Invalid table selection.")
        except ValueError:
            print("❌ Please enter a valid number.")

    except mysql.connector.Error as err:
        print(f"❌ Database connection failed: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

if __name__ == "__main__":
    main()
