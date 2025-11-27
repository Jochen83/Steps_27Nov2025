import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
from PIL import Image
import pytesseract
import os
import sqlite3
from datetime import datetime
import pdfplumber

# Kombiniertes OCR & PDF Text Extraktion Tool mit Datenbankanbindung
# Erstellt am 26.11.2025

class UnifiedTextExtractorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ruder-Regatta OCR & PDF Extraktor")
        self.root.geometry("650x850")

        # --- KONFIGURATION FÜR WINDOWS TESSERACT ---
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

        # Variablen
        self.dateipfade = []
        self.alle_ergebnisse = []
        self.verarbeitungsmodus = "Bild (OCR)"  # Default
        
        # Datenbank initialisieren
        self.db_name = "regatta_unified.db"
        self.init_database()

        # GUI Elemente
        # Modus-Auswahl Frame
        modus_frame = tk.Frame(root, bg="#e0e0e0", pady=10)
        modus_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(modus_frame, text="Verarbeitungsmodus:", font=("Arial", 11, "bold"), bg="#e0e0e0").pack(side=tk.LEFT, padx=10)
        
        self.modus_var = tk.StringVar(value="Bild (OCR)")
        
        rb_ocr = tk.Radiobutton(modus_frame, text="🖼️ Bild (OCR)", variable=self.modus_var, 
                                value="Bild (OCR)", command=self.modus_geaendert,
                                font=("Arial", 10), bg="#e0e0e0")
        rb_ocr.pack(side=tk.LEFT, padx=10)
        
        rb_pdf = tk.Radiobutton(modus_frame, text="📄 PDF", variable=self.modus_var, 
                                value="PDF", command=self.modus_geaendert,
                                font=("Arial", 10), bg="#e0e0e0")
        rb_pdf.pack(side=tk.LEFT, padx=10)
        
        # Info Label
        self.lbl_info = tk.Label(root, text="Schritt 1: Modus wählen und Dateien auswählen", font=("Arial", 12))
        self.lbl_info.pack(pady=10)

        # Button: Dateien auswählen
        self.btn_select = tk.Button(root, text="📁 Dateien auswählen", command=self.dateien_auswaehlen, 
                                    bg="#dddddd", height=2, font=("Arial", 10))
        self.btn_select.pack(fill=tk.X, padx=20, pady=5)

        self.lbl_selected = tk.Label(root, text="Keine Dateien ausgewählt", fg="grey")
        self.lbl_selected.pack(pady=5)

        # Button: Prozess starten
        self.btn_process = tk.Button(root, text="▶️ Verarbeitung starten", command=self.prozess_starten, 
                                     bg="#aaccff", height=2, state=tk.DISABLED, font=("Arial", 10, "bold"))
        self.btn_process.pack(fill=tk.X, padx=20, pady=5)

        # Textfeld für Vorschau/Log
        tk.Label(root, text="Verarbeitungs-Log:", font=("Arial", 10)).pack(anchor=tk.W, padx=20, pady=(10,0))
        self.txt_output = scrolledtext.ScrolledText(root, height=10)
        self.txt_output.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        # Button: Aktuellen Durchlauf Exportieren
        self.btn_export = tk.Button(root, text="💾 Aktuelle Ergebnisse als .txt exportieren", 
                                    command=self.exportieren, bg="#aaffaa", height=2, 
                                    state=tk.DISABLED, font=("Arial", 9))
        self.btn_export.pack(fill=tk.X, padx=20, pady=5)
        
        # Separator
        ttk.Separator(root, orient='horizontal').pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(root, text="Datenbank-Verwaltung:", font=("Arial", 10, "bold")).pack(anchor=tk.W, padx=20)
        
        # DB Buttons Frame
        db_frame = tk.Frame(root)
        db_frame.pack(fill=tk.X, padx=20, pady=5)
        
        # Button: DB Anzeigen
        self.btn_show_db = tk.Button(db_frame, text="👁️ Datenbank anzeigen", 
                                     command=self.show_database, bg="#ffddaa", height=2)
        self.btn_show_db.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Button: DB Exportieren (alle Felder)
        self.btn_export_db = tk.Button(db_frame, text="📊 Kompletter DB-Export (alle Felder)", 
                                       command=self.export_database_complete, bg="#ffccff", height=2)
        self.btn_export_db.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Button: DB Löschen
        self.btn_clear_db = tk.Button(db_frame, text="🗑️ DB löschen", 
                                      command=self.clear_database, bg="#ffaaaa", height=2)
        self.btn_clear_db.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))

    def init_database(self):
        """Erstellt die Datenbank und Tabelle falls nicht vorhanden"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS extracted_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dateiname TEXT NOT NULL,
                quellentyp TEXT NOT NULL,
                seite_nummer INTEGER,
                zeile_nummer INTEGER,
                zeile_inhalt TEXT,
                zeichen_anzahl INTEGER,
                verarbeitet_am TIMESTAMP,
                status TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def modus_geaendert(self):
        """Wird aufgerufen wenn der Verarbeitungsmodus geändert wird"""
        self.verarbeitungsmodus = self.modus_var.get()
        if self.verarbeitungsmodus == "Bild (OCR)":
            self.lbl_info.config(text="Modus: Bild (OCR) - Wählen Sie Bilddateien aus")
        else:
            self.lbl_info.config(text="Modus: PDF - Wählen Sie PDF-Dateien aus")
        
        # Reset selection
        self.dateipfade = []
        self.lbl_selected.config(text="Keine Dateien ausgewählt", fg="grey")
        self.btn_process.config(state=tk.DISABLED)
        
    def save_to_database(self, dateiname, quellentyp, seite_nr, text):
        """Speichert Ergebnisse zeilenweise in die Datenbank"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Text in Zeilen aufteilen
        zeilen = text.split('\n')
        
        for zeile_nr, zeile in enumerate(zeilen, start=1):
            cursor.execute('''
                INSERT INTO extracted_data 
                (dateiname, quellentyp, seite_nummer, zeile_nummer, zeile_inhalt, zeichen_anzahl, verarbeitet_am, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                dateiname,
                quellentyp,
                seite_nr,
                zeile_nr,
                zeile.strip(),
                len(zeile.strip()),
                datetime.now(),
                'verarbeitet'
            ))
        
        conn.commit()
        conn.close()
        
    def show_database(self):
        """Zeigt den Inhalt der Datenbank an"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM extracted_data')
            anzahl = cursor.fetchone()[0]
            
            cursor.execute('''
                SELECT id, dateiname, quellentyp, seite_nummer, zeile_nummer, zeile_inhalt, verarbeitet_am 
                FROM extracted_data 
                ORDER BY id DESC 
                LIMIT 50
            ''')
            rows = cursor.fetchall()
            
            conn.close()
            
            # Ausgabe im Textfeld
            self.txt_output.delete(1.0, tk.END)
            self.txt_output.insert(tk.END, f"=== DATENBANK: {anzahl} Zeilen gespeichert ===\n\n")
            
            if rows:
                for row in rows:
                    seite_info = f" | Seite: {row[3]}" if row[3] else ""
                    self.txt_output.insert(tk.END, 
                        f"ID: {row[0]} | Typ: {row[2]} | Datei: {row[1]}{seite_info} | Zeile: {row[4]}\n"
                        f"Inhalt: {row[5]}\n"  # Vollständiger Inhalt ohne Kürzung
                        f"Zeit: {row[6]}\n"
                        + "-"*60 + "\n"
                    )
            else:
                self.txt_output.insert(tk.END, "Keine Daten in der Datenbank.\n")
                
        except Exception as e:
            messagebox.showerror("Datenbankfehler", f"Fehler beim Lesen der DB:\n{str(e)}")

    def export_database_complete(self):
        """Exportiert die gesamte Datenbank mit ALLEN Feldern als TXT-Datei"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM extracted_data')
            anzahl = cursor.fetchone()[0]
            
            if anzahl == 0:
                messagebox.showinfo("Keine Daten", "Die Datenbank ist leer.")
                conn.close()
                return
            
            cursor.execute('''
                SELECT id, dateiname, quellentyp, seite_nummer, zeile_nummer, zeile_inhalt, 
                       zeichen_anzahl, verarbeitet_am, status
                FROM extracted_data 
                ORDER BY dateiname, quellentyp, seite_nummer, zeile_nummer ASC
            ''')
            rows = cursor.fetchall()
            conn.close()
            
            # Datei-Dialog
            dateipfad = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Textdatei", "*.txt"), ("CSV-Datei", "*.csv")],
                title="Kompletten Datenbank-Export speichern"
            )
            
            if dateipfad:
                # Bestimme Format anhand Dateiendung
                is_csv = dateipfad.lower().endswith('.csv')
                
                with open(dateipfad, 'w', encoding='utf-8') as f:
                    if is_csv:
                        # CSV Format mit Semikolon und Feldqualifizierern
                        f.write('"id";"dateiname";"quellentyp";"seite_nummer";"zeile_nummer";"zeile_inhalt";"zeichen_anzahl";"verarbeitet_am";"status"\n')
                        
                        for row in rows:
                            # Felder mit Anführungszeichen escapen
                            escaped_row = []
                            for value in row:
                                if value is None:
                                    escaped_row.append('""')
                                else:
                                    # Anführungszeichen verdoppeln
                                    escaped_value = str(value).replace('"', '""')
                                    escaped_row.append(f'"{escaped_value}"')
                            f.write(";".join(escaped_row) + "\n")
                    else:
                        # TXT Format - strukturiert
                        # Feldnamen als Kopfzeile
                        f.write("ID;Dateiname;Typ;Seite;Zeile;Inhalt;Zeichen;Verarbeitet am;Status\n")
                        
                        for row in rows:
                            id_val, dateiname, quellentyp, seite_nr, zeile_nr, inhalt, zeichen, zeit, status = row
                            
                            # Zeile mit allen Feldern - VOLLSTÄNDIGER Inhalt
                            seite_str = str(seite_nr) if seite_nr else "-"
                            inhalt_voll = inhalt if inhalt else ""
                            
                            f.write(f"{id_val};{dateiname};{quellentyp};{seite_str};{zeile_nr};{inhalt_voll};{zeichen};{zeit};{status}\n")
                
                messagebox.showinfo("Export erfolgreich", 
                    f"Datenbank erfolgreich exportiert:\n{dateipfad}\n\n{anzahl} Einträge mit allen Feldern")
                
                # Frage ob Datei geöffnet werden soll
                oeffnen = messagebox.askyesno("Datei öffnen?", "Möchten Sie die Datei jetzt öffnen?")
                if oeffnen:
                    os.startfile(dateipfad)
                
        except Exception as e:
            messagebox.showerror("Export-Fehler", f"Fehler beim Exportieren:\n{str(e)}")

    def clear_database(self):
        """Löscht alle Einträge aus der Datenbank nach Bestätigung"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM extracted_data')
            anzahl = cursor.fetchone()[0]
            
            conn.close()
            
            if anzahl == 0:
                messagebox.showinfo("Datenbank leer", "Die Datenbank enthält keine Einträge.")
                return
            
            antwort = messagebox.askyesno(
                "Datenbank löschen?",
                f"Möchten Sie wirklich ALLE {anzahl} Einträge löschen?\n\n"
                "Diese Aktion kann NICHT rückgängig gemacht werden!",
                icon='warning'
            )
            
            if antwort:
                final_check = messagebox.askyesno(
                    "Letzte Bestätigung",
                    f"LETZTE WARNUNG: {anzahl} Einträge werden unwiderruflich gelöscht!\n\n"
                    "Wirklich fortfahren?",
                    icon='warning'
                )
                
                if final_check:
                    conn = sqlite3.connect(self.db_name)
                    cursor = conn.cursor()
                    
                    cursor.execute('DELETE FROM extracted_data')
                    cursor.execute('DELETE FROM sqlite_sequence WHERE name="extracted_data"')
                    
                    conn.commit()
                    conn.close()
                    
                    self.txt_output.delete(1.0, tk.END)
                    self.txt_output.insert(tk.END, f"Datenbank wurde geleert.\n{anzahl} Einträge gelöscht.\n")
                    
                    messagebox.showinfo("Erfolgreich", f"Datenbank wurde geleert.\n{anzahl} Einträge gelöscht.")
                    
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Löschen der Datenbank:\n{str(e)}")

    def dateien_auswaehlen(self):
        """Dateidialog öffnen je nach Modus"""
        if self.verarbeitungsmodus == "Bild (OCR)":
            files = filedialog.askopenfilenames(
                title="Bilder auswählen",
                filetypes=[
                    ("Bilddateien", "*.jpg *.jpeg *.png *.bmp *.tiff *.jpf"),
                    ("Alle Dateien", "*.*")
                ]
            )
        else:  # PDF
            files = filedialog.askopenfilenames(
                title="PDF-Dateien auswählen",
                filetypes=[
                    ("PDF-Dateien", "*.pdf"),
                    ("Alle Dateien", "*.*")
                ]
            )
        
        if files:
            self.dateipfade = list(files)
            anzahl = len(self.dateipfade)
            self.lbl_selected.config(text=f"{anzahl} Datei(en) ausgewählt.", fg="black")
            self.btn_process.config(state=tk.NORMAL)
            self.txt_output.insert(tk.END, f"Bereit zum Verarbeiten von {anzahl} {self.verarbeitungsmodus}-Dateien.\n")
        else:
            self.lbl_selected.config(text="Keine neuen Dateien ausgewählt.")

    def prozess_starten(self):
        """Startet die Verarbeitung je nach Modus"""
        self.alle_ergebnisse = []
        self.txt_output.delete(1.0, tk.END)
        
        self.btn_process.config(state=tk.DISABLED)
        self.root.update()

        if self.verarbeitungsmodus == "Bild (OCR)":
            self.verarbeite_bilder()
        else:
            self.verarbeite_pdfs()

        self.txt_output.insert(tk.END, "\n✅ Fertig! Alle Dateien wurden verarbeitet.\n")
        self.btn_export.config(state=tk.NORMAL)
        self.btn_process.config(state=tk.NORMAL)
        messagebox.showinfo("Fertig", f"Alle {self.verarbeitungsmodus}-Dateien wurden verarbeitet.")

    def verarbeite_bilder(self):
        """OCR-Verarbeitung für Bilder"""
        for pfad in self.dateipfade:
            dateiname = os.path.basename(pfad)
            self.txt_output.insert(tk.END, f"🖼️ OCR: {dateiname}...\n")
            self.root.update()

            try:
                img = Image.open(pfad)
                custom_config = r'--oem 3 --psm 6'
                text = pytesseract.image_to_string(img, lang='deu', config=custom_config)
                
                ergebnis_eintrag = f"--- DATEI: {dateiname} (OCR) ---\n{text}\n" + ("="*40) + "\n"
                self.alle_ergebnisse.append(ergebnis_eintrag)
                
                # In Datenbank speichern
                self.save_to_database(dateiname, 'OCR', None, text)
                
                self.txt_output.insert(tk.END, f"   ✓ OK ({len(text)} Zeichen, in DB gespeichert)\n")
                
            except Exception as e:
                fehler_msg = f"   ✗ FEHLER bei {dateiname}: {str(e)}\n"
                self.alle_ergebnisse.append(fehler_msg)
                self.txt_output.insert(tk.END, fehler_msg)

    def verarbeite_pdfs(self):
        """PDF-Textextraktion"""
        for pfad in self.dateipfade:
            dateiname = os.path.basename(pfad)
            self.txt_output.insert(tk.END, f"📄 PDF: {dateiname}...\n")
            self.root.update()

            try:
                with pdfplumber.open(pfad) as pdf:
                    total_pages = len(pdf.pages)
                    gesamter_text = ""
                    
                    for seite_nr, page in enumerate(pdf.pages, start=1):
                        text = page.extract_text()
                        
                        if text:
                            self.save_to_database(dateiname, 'PDF', seite_nr, text)
                            gesamter_text += f"\n--- Seite {seite_nr} ---\n{text}\n"
                        else:
                            self.txt_output.insert(tk.END, f"   ⚠ Seite {seite_nr}: Kein Text\n")
                        
                        self.root.update()
                
                ergebnis_eintrag = f"--- DATEI: {dateiname} (PDF, {total_pages} Seiten) ---\n{gesamter_text}\n" + ("="*40) + "\n"
                self.alle_ergebnisse.append(ergebnis_eintrag)
                
                self.txt_output.insert(tk.END, f"   ✓ OK ({len(gesamter_text)} Zeichen, {total_pages} Seiten, in DB gespeichert)\n")
                
            except Exception as e:
                fehler_msg = f"   ✗ FEHLER bei {dateiname}: {str(e)}\n"
                self.alle_ergebnisse.append(fehler_msg)
                self.txt_output.insert(tk.END, fehler_msg)

    def exportieren(self):
        """Exportiert die aktuellen Ergebnisse"""
        if not self.alle_ergebnisse:
            return

        dateipfad = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Textdatei", "*.txt")],
            title="Aktuelle Ergebnisse speichern"
        )

        if dateipfad:
            try:
                with open(dateipfad, 'w', encoding='utf-8') as f:
                    for eintrag in self.alle_ergebnisse:
                        f.write(eintrag)
                        f.write("\n")
                
                messagebox.showinfo("Gespeichert", f"Datei erfolgreich gespeichert unter:\n{dateipfad}")
                
                oeffnen = messagebox.askyesno("Datei öffnen?", "Möchten Sie die Datei jetzt im Editor öffnen?")
                if oeffnen:
                    os.startfile(dateipfad)
                    
            except Exception as e:
                messagebox.showerror("Fehler beim Speichern", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = UnifiedTextExtractorApp(root)
    root.mainloop()
