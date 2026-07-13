from database.connection import get_connection

try:
    conn = get_connection()
    print("✅ Connected to Supabase successfully!")
    conn.close()
except Exception as e:
    print(f"❌ Connection failed: {e}")