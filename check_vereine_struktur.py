import sqlite3

# Verbindung zur Datenbank
conn = sqlite3.connect('regatta_unified.db')
cursor = conn.cursor()

# Tabellenstruktur der Vereine-Tabelle abrufen
cursor.execute('PRAGMA table_info(Vereine)')
columns = cursor.fetchall()

print("Spalten der Tabelle 'Vereine':")
print("-" * 50)
for col in columns:
    col_id = col[0]
    col_name = col[1]
    col_type = col[2]
    not_null = col[3]
    default_value = col[4]
    primary_key = col[5]
    
    nullable = "No" if not_null else "Yes"
    pk_marker = " (PRIMARY KEY)" if primary_key else ""
    
    print(f"{col_name}: {col_type} (nullable: {nullable}){pk_marker}")

# Spezifisch nach Verein_DRVID suchen
cursor.execute('PRAGMA table_info(Vereine)')
for col in cursor.fetchall():
    if col[1] == 'Verein_DRVID':
        print(f"\n🔍 Feld 'Verein_DRVID' gefunden:")
        print(f"   Typ: {col[2]}")
        print(f"   Nullable: {'No' if col[3] else 'Yes'}")
        print(f"   Default: {col[4] if col[4] else 'None'}")
        break
else:
    print(f"\n❌ Feld 'Verein_DRVID' nicht in Tabelle 'Vereine' gefunden")

# Einige Beispielwerte anzeigen
print(f"\n📋 Beispielwerte aus der Tabelle 'Vereine':")
cursor.execute('SELECT * FROM Vereine LIMIT 5')
rows = cursor.fetchall()

# Spaltennamen holen
cursor.execute('PRAGMA table_info(Vereine)')
column_names = [col[1] for col in cursor.fetchall()]

for row in rows:
    print(f"Zeile: {dict(zip(column_names, row))}")

conn.close()