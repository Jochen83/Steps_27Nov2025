import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import os
import sqlite3
from datetime import datetime

# Tabellen-Import Tool für regatta_unified.db
# Erstellt am 27.11.2025

class TabellImportApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tabellen-Import aus TXT-Dateien")
        self.root.geometry("700x600")
        
        # Variablen
        self.db_name = "regatta_unified.db"
        self.ausgewaehlte_datei = None
        self.feldnamen = []
        self.tabellenname = ""
        
        # GUI Elemente
        # Titel
        titel_label = tk.Label(root, text="Tabellen-Import aus TXT-Dateien", 
                               font=("Arial", 14, "bold"), bg="#e0f7fa", pady=10)
        titel_label.pack(fill=tk.X)
        
        # Info Label
        info_frame = tk.Frame(root, bg="#fff9c4", pady=5)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(info_frame, text="📋 Importiert TXT-Dateien mit Kopfzeile in SQLite-Datenbank", 
                 font=("Arial", 9), bg="#fff9c4").pack()
        
        # Button: TXT-Datei auswählen
        self.btn_select = tk.Button(root, text="📁 TXT-Datei auswählen", 
                                    command=self.datei_auswaehlen, 
                                    bg="#b3e5fc", height=2, font=("Arial", 11, "bold"))
        self.btn_select.pack(fill=tk.X, padx=20, pady=10)
        
        # Ausgewählte Datei anzeigen
        self.lbl_datei = tk.Label(root, text="Keine Datei ausgewählt", fg="grey", font=("Arial", 9))
        self.lbl_datei.pack(pady=5)
        
        # Frame für Tabellenname
        tabellen_frame = tk.Frame(root)
        tabellen_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(tabellen_frame, text="Tabellenname:", font=("Arial", 10)).pack(side=tk.LEFT, padx=(0, 10))
        self.entry_tabellenname = tk.Entry(tabellen_frame, font=("Arial", 10), width=30)
        self.entry_tabellenname.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Vorschau-Bereich
        tk.Label(root, text="Vorschau (erste 10 Zeilen):", font=("Arial", 10, "bold")).pack(anchor=tk.W, padx=20, pady=(10,5))
        self.txt_vorschau = scrolledtext.ScrolledText(root, height=15, font=("Courier", 9))
        self.txt_vorschau.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        
        # Button: Import durchführen
        self.btn_import = tk.Button(root, text="⬆️ In Datenbank importieren", 
                                    command=self.import_durchfuehren, 
                                    bg="#81c784", height=2, state=tk.DISABLED, 
                                    font=("Arial", 11, "bold"))
        self.btn_import.pack(fill=tk.X, padx=20, pady=10)
        
        # Statusleiste
        self.status_label = tk.Label(root, text="Bereit", bg="#e0e0e0", anchor=tk.W, font=("Arial", 9))
        self.status_label.pack(fill=tk.X, side=tk.BOTTOM)
    
    def datei_auswaehlen(self):
        """Öffnet Dateidialog zur Auswahl einer TXT-Datei"""
        datei = filedialog.askopenfilename(
            title="TXT-Datei mit Kopfzeile auswählen",
            filetypes=[
                ("Textdateien", "*.txt"),
                ("CSV-Dateien", "*.csv"),
                ("Alle Dateien", "*.*")
            ]
        )
        
        if datei:
            self.ausgewaehlte_datei = datei
            dateiname = os.path.basename(datei)
            self.lbl_datei.config(text=f"Ausgewählt: {dateiname}", fg="black")
            
            # Automatisch Tabellenname vorschlagen (ohne Erweiterung)
            vorgeschlagener_name = os.path.splitext(dateiname)[0].replace(" ", "_").replace("-", "_")
            self.entry_tabellenname.delete(0, tk.END)
            self.entry_tabellenname.insert(0, vorgeschlagener_name)
            
            # Datei analysieren und Vorschau anzeigen
            self.datei_analysieren()
    
    def datei_analysieren(self):
        """Liest die Datei ein und zeigt eine Vorschau"""
        try:
            with open(self.ausgewaehlte_datei, 'r', encoding='utf-8') as f:
                zeilen = f.readlines()
            
            if len(zeilen) == 0:
                messagebox.showerror("Fehler", "Die Datei ist leer!")
                return
            
            # Erste Zeile als Kopfzeile verwenden
            kopfzeile = zeilen[0].strip()
            
            # Feldtrenner erkennen (Semikolon oder Tab)
            if ';' in kopfzeile:
                trennzeichen = ';'
            elif '\t' in kopfzeile:
                trennzeichen = '\t'
            else:
                messagebox.showerror("Fehler", "Kein Feldtrenner gefunden (Semikolon oder Tab erwartet)!")
                return
            
            # Feldnamen extrahieren
            self.feldnamen = [feld.strip().strip('"') for feld in kopfzeile.split(trennzeichen)]
            
            # Vorschau erstellen
            self.txt_vorschau.delete(1.0, tk.END)
            self.txt_vorschau.insert(tk.END, f"=== FELDNAMEN ({len(self.feldnamen)} Felder) ===\n")
            self.txt_vorschau.insert(tk.END, f"{', '.join(self.feldnamen)}\n\n")
            self.txt_vorschau.insert(tk.END, f"=== VORSCHAU (erste 10 Zeilen) ===\n")
            
            # Erste 10 Datenzeilen anzeigen
            for i, zeile in enumerate(zeilen[1:11], start=1):
                self.txt_vorschau.insert(tk.END, f"Zeile {i}: {zeile}")
            
            anzahl_zeilen = len(zeilen) - 1  # -1 für Kopfzeile
            self.txt_vorschau.insert(tk.END, f"\n\n=== STATISTIK ===\n")
            self.txt_vorschau.insert(tk.END, f"Gesamt: {anzahl_zeilen} Datenzeilen\n")
            self.txt_vorschau.insert(tk.END, f"Feldtrenner: '{trennzeichen}'\n")
            
            # Import-Button aktivieren
            self.btn_import.config(state=tk.NORMAL)
            self.status_label.config(text=f"Bereit zum Import: {anzahl_zeilen} Zeilen, {len(self.feldnamen)} Felder")
            
        except Exception as e:
            messagebox.showerror("Fehler beim Lesen", f"Fehler beim Analysieren der Datei:\n{str(e)}")
            self.btn_import.config(state=tk.DISABLED)
    
    def import_durchfuehren(self):
        """Importiert die Daten in die SQLite-Datenbank"""
        # Tabellenname validieren
        self.tabellenname = self.entry_tabellenname.get().strip()
        
        if not self.tabellenname:
            messagebox.showerror("Fehler", "Bitte geben Sie einen Tabellennamen ein!")
            return
        
        # Ungültige Zeichen ersetzen
        self.tabellenname = ''.join(c if c.isalnum() or c == '_' else '_' for c in self.tabellenname)
        
        # Bestätigung
        antwort = messagebox.askyesno(
            "Import bestätigen",
            f"Tabelle '{self.tabellenname}' mit {len(self.feldnamen)} Feldern erstellen?\n\n"
            f"Datei: {os.path.basename(self.ausgewaehlte_datei)}\n\n"
            "Vorhandene Tabelle wird überschrieben!"
        )
        
        if not antwort:
            return
        
        try:
            # Datei einlesen
            with open(self.ausgewaehlte_datei, 'r', encoding='utf-8') as f:
                zeilen = f.readlines()
            
            # Feldtrenner erkennen
            kopfzeile = zeilen[0].strip()
            trennzeichen = ';' if ';' in kopfzeile else '\t'
            
            # Datenbank-Verbindung
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Alte Tabelle löschen falls vorhanden
            cursor.execute(f'DROP TABLE IF EXISTS {self.tabellenname}')
            
            # Feldnamen für SQL aufbereiten (ungültige Zeichen ersetzen)
            feldnamen_sql = []
            for feld in self.feldnamen:
                feld_clean = ''.join(c if c.isalnum() or c == '_' else '_' for c in feld)
                feldnamen_sql.append(feld_clean)
            
            # CREATE TABLE Statement erstellen (alle Felder als TEXT)
            felder_definition = ', '.join([f'"{feld}" TEXT' for feld in feldnamen_sql])
            create_sql = f'CREATE TABLE {self.tabellenname} (id INTEGER PRIMARY KEY AUTOINCREMENT, {felder_definition})'
            
            cursor.execute(create_sql)
            
            # Daten importieren
            platzhalter = ', '.join(['?' for _ in feldnamen_sql])
            insert_sql = f'INSERT INTO {self.tabellenname} ({", ".join([f"{feld}" for feld in feldnamen_sql])}) VALUES ({platzhalter})'
            
            importiert = 0
            fehler = 0
            
            for i, zeile in enumerate(zeilen[1:], start=2):  # Ab Zeile 2 (nach Kopfzeile)
                zeile = zeile.strip()
                if not zeile:
                    continue
                
                # Felder aufteilen
                werte = zeile.split(trennzeichen)
                
                # Anführungszeichen entfernen falls vorhanden
                werte = [w.strip().strip('"').replace('""', '"') for w in werte]
                
                # Fehlende Felder mit None auffüllen
                while len(werte) < len(feldnamen_sql):
                    werte.append(None)
                
                # Überschüssige Felder abschneiden
                werte = werte[:len(feldnamen_sql)]
                
                try:
                    cursor.execute(insert_sql, werte)
                    importiert += 1
                except Exception as e:
                    fehler += 1
                    print(f"Fehler in Zeile {i}: {str(e)}")
            
            conn.commit()
            conn.close()
            
            # Erfolgsmeldung
            self.status_label.config(text=f"Import abgeschlossen: {importiert} Zeilen importiert, {fehler} Fehler")
            
            messagebox.showinfo(
                "Import erfolgreich",
                f"Tabelle '{self.tabellenname}' wurde erstellt!\n\n"
                f"Importiert: {importiert} Zeilen\n"
                f"Fehler: {fehler}\n"
                f"Datenbank: {self.db_name}"
            )
            
            # Vorschau aktualisieren
            self.tabelle_anzeigen()
            
        except Exception as e:
            messagebox.showerror("Import-Fehler", f"Fehler beim Import:\n{str(e)}")
            self.status_label.config(text="Import fehlgeschlagen!")
    
    def tabelle_anzeigen(self):
        """Zeigt die importierte Tabelle in der Vorschau"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute(f'SELECT COUNT(*) FROM {self.tabellenname}')
            anzahl = cursor.fetchone()[0]
            
            cursor.execute(f'SELECT * FROM {self.tabellenname} LIMIT 10')
            rows = cursor.fetchall()
            
            # Spaltennamen abrufen
            spalten = [description[0] for description in cursor.description]
            
            conn.close()
            
            # Vorschau aktualisieren
            self.txt_vorschau.delete(1.0, tk.END)
            self.txt_vorschau.insert(tk.END, f"=== TABELLE: {self.tabellenname} ({anzahl} Einträge) ===\n\n")
            self.txt_vorschau.insert(tk.END, f"Spalten: {', '.join(spalten)}\n\n")
            self.txt_vorschau.insert(tk.END, "=== ERSTE 10 EINTRÄGE ===\n")
            
            for row in rows:
                self.txt_vorschau.insert(tk.END, f"{row}\n")
            
        except Exception as e:
            print(f"Fehler beim Anzeigen: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = TabellImportApp(root)
    root.mainloop()
