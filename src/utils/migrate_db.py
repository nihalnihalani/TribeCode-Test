import sqlite3
import os

DB_PATH = "vibebot.db"

def migrate():
    if not os.path.exists(DB_PATH):
        print("No DB found, init_db will create it.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check existing columns
    cursor.execute("PRAGMA table_info(interactions)")
    columns = [info[1] for info in cursor.fetchall()]
    
    new_columns = {
        "author_name": "TEXT",
        "author_handle": "TEXT",
        "post_url": "TEXT",
        "metrics_json": "TEXT",
        "media_url": "TEXT"
    }
    
    for col, dtype in new_columns.items():
        if col not in columns:
            print(f"Adding column {col}...")
            try:
                cursor.execute(f"ALTER TABLE interactions ADD COLUMN {col} {dtype}")
            except Exception as e:
                print(f"Error adding {col}: {e}")
                
    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == "__main__":
    migrate()

