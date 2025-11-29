import sqlite3
import os

# Prüfen ob die Datenbank-Datei existiert
db_name = "regatta_unified.db"
if os.path.exists(db_name):
    print(f"✅ Datenbankdatei '{db_name}' wurde gefunden")
    
    # Datenbank öffnen und Tabellen anzeigen
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        
        # Tabellen abfragen
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        if tables:
            print(f"\n📊 Tabellen in der Datenbank:")
            for table in tables:
                table_name = table[0]
                print(f"- {table_name}")
                
                # Anzahl Zeilen in jeder Tabelle
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"  └─ {count} Zeilen")
        else:
            print("\n⚠️  Keine Tabellen in der Datenbank gefunden")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Fehler beim Zugriff auf die Datenbank: {e}")
        
else:
    print(f"❌ Datenbankdatei '{db_name}' nicht gefunden!")
    print(f"📂 Aktuelles Verzeichnis: {os.getcwd()}")
    print("📋 Dateien im aktuellen Verzeichnis:")
    for file in os.listdir('.'):
        if file.endswith('.db'):
            print(f"  - {file}")