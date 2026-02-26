import psycopg2

conn = psycopg2.connect(
    "postgresql://postgres:sahil17raooo@db.fbevjixjdphlqlodqxyq.supabase.co:5432/postgres"
)

cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM approved_titles;")
print(cursor.fetchone())