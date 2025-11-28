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
        self.root.geometry("700x650")
        
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
        
        # Button: Tabellen anzeigen
        self.btn_tabellen = tk.Button(root, text="📊 Tabellen der Datenbank anzeigen", 
                                      command=self.tabellen_fenster_oeffnen, 
                                      bg="#ffb74d", height=2, 
                                      font=("Arial", 11, "bold"))
        self.btn_tabellen.pack(fill=tk.X, padx=20, pady=10)
        
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
            insert_sql = f'INSERT INTO {self.tabellenname} ({", ".join([f"\"{feld}\"" for feld in feldnamen_sql])}) VALUES ({platzhalter})'
            
            importiert = 0
            fehler = 0
            fehler_details = []
            
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
                    fehler_msg = f"Zeile {i}: {str(e)}"
                    fehler_details.append(fehler_msg)
                    if fehler <= 10:  # Nur erste 10 Fehler ausgeben
                        print(fehler_msg)
            
            conn.commit()
            conn.close()
            
            # Erfolgsmeldung
            self.status_label.config(text=f"Import abgeschlossen: {importiert} Zeilen importiert, {fehler} Fehler")
            
            erfolg_msg = f"Tabelle '{self.tabellenname}' wurde erstellt!\n\n" \
                        f"Importiert: {importiert} Zeilen\n" \
                        f"Fehler: {fehler}\n" \
                        f"Datenbank: {self.db_name}"
            
            if fehler > 0 and fehler_details:
                erfolg_msg += f"\n\nErste Fehler:\n" + "\n".join(fehler_details[:5])
            
            messagebox.showinfo("Import abgeschlossen", erfolg_msg)
            
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
    
    def tabellen_fenster_oeffnen(self):
        """Öffnet ein neues Fenster mit Liste aller Tabellen"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Alle Tabellen abrufen
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
            tabellen = cursor.fetchall()
            conn.close()
            
            if not tabellen:
                messagebox.showinfo("Keine Tabellen", "Die Datenbank enthält keine Tabellen.")
                return
            
            # Neues Fenster erstellen
            tabellen_window = tk.Toplevel(self.root)
            tabellen_window.title("Datenbank-Tabellen")
            tabellen_window.geometry("900x600")
            
            # Titel
            tk.Label(tabellen_window, text=f"Tabellen in {self.db_name}", 
                    font=("Arial", 12, "bold"), bg="#e1bee7", pady=10).pack(fill=tk.X)
            
            # Frame für Tabellenliste und Anzeige
            main_frame = tk.Frame(tabellen_window)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Linke Seite: Tabellenliste
            left_frame = tk.Frame(main_frame)
            left_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 5))
            
            tk.Label(left_frame, text=f"Tabellen ({len(tabellen)}):", 
                    font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=5)
            
            # Listbox für Tabellen
            list_frame = tk.Frame(left_frame)
            list_frame.pack(fill=tk.BOTH, expand=True)
            
            scrollbar = tk.Scrollbar(list_frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            tabellen_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, 
                                         font=("Arial", 10), width=30)
            tabellen_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.config(command=tabellen_listbox.yview)
            
            # Tabellen in Listbox einfügen
            for tabelle in tabellen:
                tabellen_listbox.insert(tk.END, tabelle[0])
            
            # Button: Tabelle löschen
            btn_delete = tk.Button(left_frame, text="🗑️ Ausgewählte Tabelle löschen", 
                                  command=lambda: tabelle_loeschen(tabellen_listbox, tree, info_label), 
                                  bg="#ef5350", fg="white", font=("Arial", 9, "bold"))
            btn_delete.pack(fill=tk.X, pady=(10, 0))
            
            # Button: Tabelle exportieren
            btn_export = tk.Button(left_frame, text="💾 Tabelle als TXT exportieren", 
                                  command=lambda: tabelle_exportieren(tabellen_listbox), 
                                  bg="#4caf50", fg="white", font=("Arial", 9, "bold"))
            btn_export.pack(fill=tk.X, pady=(5, 0))
            
            # Rechte Seite: Tabellenansicht mit Treeview
            right_frame = tk.Frame(main_frame)
            right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
            
            # Info-Label
            info_label = tk.Label(right_frame, text="Wählen Sie eine Tabelle aus", 
                                 font=("Arial", 10, "italic"), fg="grey")
            info_label.pack(anchor=tk.W, pady=5)
            
            # Frame für Treeview
            tree_frame = tk.Frame(right_frame)
            tree_frame.pack(fill=tk.BOTH, expand=True)
            
            # Scrollbars für Treeview
            vsb = tk.Scrollbar(tree_frame, orient="vertical")
            vsb.pack(side=tk.RIGHT, fill=tk.Y)
            
            hsb = tk.Scrollbar(tree_frame, orient="horizontal")
            hsb.pack(side=tk.BOTTOM, fill=tk.X)
            
            # Treeview erstellen
            tree = ttk.Treeview(tree_frame, yscrollcommand=vsb.set, xscrollcommand=hsb.set)
            tree.pack(fill=tk.BOTH, expand=True)
            
            vsb.config(command=tree.yview)
            hsb.config(command=tree.xview)
            
            # Variable für aktuelle Sortierung
            sort_data = {'column': None, 'reverse': False, 'tabelle': None, 'daten': []}
            
            def tabelle_loeschen(listbox, treeview, info_lbl):
                """Löscht die ausgewählte Tabelle aus der Datenbank"""
                selection = listbox.curselection()
                if not selection:
                    messagebox.showwarning("Keine Auswahl", "Bitte wählen Sie zuerst eine Tabelle aus.")
                    return
                
                tabellen_name = listbox.get(selection[0])
                
                # Sicherheitsabfrage
                antwort = messagebox.askyesno(
                    "Tabelle löschen?",
                    f"Möchten Sie die Tabelle '{tabellen_name}' wirklich LÖSCHEN?\n\n"
                    "Diese Aktion kann NICHT rückgängig gemacht werden!",
                    icon='warning'
                )
                
                if not antwort:
                    return
                
                # Finale Bestätigung
                final = messagebox.askyesno(
                    "Letzte Bestätigung",
                    f"LETZTE WARNUNG:\n\n"
                    f"Tabelle '{tabellen_name}' wird unwiderruflich gelöscht!\n\n"
                    "Wirklich fortfahren?",
                    icon='warning'
                )
                
                if not final:
                    return
                
                try:
                    conn = sqlite3.connect(self.db_name)
                    cursor = conn.cursor()
                    
                    cursor.execute(f'DROP TABLE IF EXISTS {tabellen_name}')
                    
                    conn.commit()
                    conn.close()
                    
                    # Listbox aktualisieren
                    listbox.delete(selection[0])
                    
                    # Treeview leeren
                    for item in treeview.get_children():
                        treeview.delete(item)
                    
                    treeview["columns"] = []
                    
                    # Info aktualisieren
                    info_lbl.config(text=f"Tabelle '{tabellen_name}' wurde gelöscht")
                    
                    messagebox.showinfo("Erfolgreich", f"Tabelle '{tabellen_name}' wurde gelöscht.")
                    
                except Exception as e:
                    messagebox.showerror("Fehler", f"Fehler beim Löschen der Tabelle:\n{str(e)}")
            
            def tabelle_exportieren(listbox):
                """Exportiert die ausgewählte Tabelle als TXT-Datei"""
                selection = listbox.curselection()
                if not selection:
                    messagebox.showwarning("Keine Auswahl", "Bitte wählen Sie zuerst eine Tabelle aus.")
                    return
                
                tabellen_name = listbox.get(selection[0])
                
                try:
                    conn = sqlite3.connect(self.db_name)
                    cursor = conn.cursor()
                    
                    # Prüfen ob Tabelle existiert
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (tabellen_name,))
                    if not cursor.fetchone():
                        messagebox.showerror("Fehler", f"Tabelle '{tabellen_name}' nicht gefunden!")
                        conn.close()
                        return
                    
                    # Tabellenstruktur abrufen
                    cursor.execute(f'PRAGMA table_info("{tabellen_name}")')
                    spalten_info = cursor.fetchall()
                    spalten = [info[1] for info in spalten_info]
                    
                    # Alle Daten abrufen - mit Anführungszeichen um Tabellenname
                    cursor.execute(f'SELECT * FROM "{tabellen_name}"')
                    rows = cursor.fetchall()
                    
                    cursor.execute(f'SELECT COUNT(*) FROM "{tabellen_name}"')
                    anzahl = cursor.fetchone()[0]
                    
                    conn.close()
                    
                    if anzahl == 0:
                        messagebox.showinfo("Keine Daten", f"Die Tabelle '{tabellen_name}' enthält keine Daten.")
                        return
                    
                    # Datei-Dialog
                    dateipfad = filedialog.asksaveasfilename(
                        defaultextension=".txt",
                        filetypes=[("Textdatei", "*.txt"), ("CSV-Datei", "*.csv")],
                        title=f"Tabelle '{tabellen_name}' exportieren"
                    )
                    
                    if dateipfad:
                        # Bestimme Format anhand Dateiendung
                        is_csv = dateipfad.lower().endswith('.csv')
                        
                        with open(dateipfad, 'w', encoding='utf-8') as f:
                            if is_csv:
                                # CSV Format mit Semikolon
                                # Kopfzeile
                                kopfzeile = ";".join([f'"{spalte}"' for spalte in spalten])
                                f.write(kopfzeile + "\n")
                                
                                # Datenzeilen
                                for row in rows:
                                    zeile_werte = []
                                    for wert in row:
                                        if wert is None:
                                            zeile_werte.append('""')
                                        else:
                                            # Anführungszeichen escapen
                                            escaped_value = str(wert).replace('"', '""')
                                            zeile_werte.append(f'"{escaped_value}"')
                                    f.write(";".join(zeile_werte) + "\n")
                            else:
                                # TXT Format mit Semikolon
                                # Kopfzeile
                                kopfzeile = ";".join(spalten)
                                f.write(kopfzeile + "\n")
                                
                                # Datenzeilen
                                for row in rows:
                                    zeile_werte = [str(wert) if wert is not None else "" for wert in row]
                                    f.write(";".join(zeile_werte) + "\n")
                        
                        messagebox.showinfo("Export erfolgreich", 
                                           f"Tabelle '{tabellen_name}' erfolgreich exportiert:\n{dateipfad}\n\n"
                                           f"{anzahl} Zeilen, {len(spalten)} Spalten")
                        
                        # Frage ob Datei geöffnet werden soll
                        oeffnen = messagebox.askyesno("Datei öffnen?", "Möchten Sie die Datei jetzt öffnen?")
                        if oeffnen:
                            os.startfile(dateipfad)
                
                except Exception as e:
                    messagebox.showerror("Export-Fehler", f"Fehler beim Exportieren der Tabelle:\n{str(e)}")
            
            def tabelle_anzeigen(event):
                """Zeigt die ausgewählte Tabelle im Treeview an"""
                selection = tabellen_listbox.curselection()
                if not selection:
                    return
                
                tabellen_name = tabellen_listbox.get(selection[0])
                
                try:
                    conn = sqlite3.connect(self.db_name)
                    cursor = conn.cursor()
                    
                    # Tabellenstruktur abrufen
                    cursor.execute(f'PRAGMA table_info({tabellen_name})')
                    spalten_info = cursor.fetchall()
                    spalten = [info[1] for info in spalten_info]
                    
                    # Daten abrufen
                    cursor.execute(f'SELECT * FROM {tabellen_name}')
                    rows = cursor.fetchall()
                    
                    cursor.execute(f'SELECT COUNT(*) FROM {tabellen_name}')
                    anzahl = cursor.fetchone()[0]
                    
                    conn.close()
                    
                    # Treeview leeren
                    for item in tree.get_children():
                        tree.delete(item)
                    
                    # Spalten konfigurieren
                    tree["columns"] = spalten
                    tree["show"] = "headings"
                    
                    # Spaltenüberschriften mit Sortier-Funktion
                    for col in spalten:
                        tree.heading(col, text=col, 
                                   command=lambda c=col: sortiere_spalte(c, False))
                        tree.column(col, width=100, anchor=tk.W)
                    
                    # Daten in Treeview einfügen
                    for row in rows:
                        tree.insert("", tk.END, values=row)
                    
                    # Sort-Daten speichern
                    sort_data['tabelle'] = tabellen_name
                    sort_data['daten'] = rows
                    sort_data['column'] = None
                    sort_data['reverse'] = False
                    
                    # Info aktualisieren
                    info_label.config(text=f"Tabelle: {tabellen_name} ({anzahl} Einträge, {len(spalten)} Spalten)")
                    
                except Exception as e:
                    messagebox.showerror("Fehler", f"Fehler beim Laden der Tabelle:\n{str(e)}")
            
            def sortiere_spalte(col, reverse):
                """Sortiert die Treeview-Spalte"""
                try:
                    # Spaltenindex finden
                    spalten = tree["columns"]
                    col_index = list(spalten).index(col)
                    
                    # Daten aus Treeview holen
                    daten = [(tree.set(child, col), child) for child in tree.get_children("")]
                    
                    # Versuche numerisch zu sortieren, sonst alphabetisch
                    try:
                        daten.sort(key=lambda t: float(t[0]) if t[0] else 0, reverse=reverse)
                    except (ValueError, TypeError):
                        daten.sort(key=lambda t: str(t[0]).lower(), reverse=reverse)
                    
                    # Neu anordnen
                    for index, (val, child) in enumerate(daten):
                        tree.move(child, "", index)
                    
                    # Sortier-Indikator in Überschrift
                    pfeil = " ▼" if reverse else " ▲"
                    
                    # Alle Überschriften zurücksetzen
                    for spalte in spalten:
                        tree.heading(spalte, text=spalte.replace(" ▲", "").replace(" ▼", ""),
                                   command=lambda c=spalte: sortiere_spalte(c, False))
                    
                    # Aktuelle Spalte mit Pfeil
                    tree.heading(col, text=col + pfeil,
                               command=lambda: sortiere_spalte(col, not reverse))
                    
                except Exception as e:
                    print(f"Fehler beim Sortieren: {str(e)}")
            
            # Event-Binding für Listbox
            tabellen_listbox.bind("<<ListboxSelect>>", tabelle_anzeigen)
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Öffnen der Tabellenliste:\n{str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = TabellImportApp(root)
    root.mainloop()
