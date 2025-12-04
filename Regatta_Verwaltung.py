import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import sqlite3
import csv
import os
import subprocess
import sys
import shutil
from datetime import datetime

# Regatta Verwaltung - Datenbankbasiert mit vollständiger Struktur aus Regatten.txt
# Alle Felder sortierbar, vollständige CRUD-Operationen
# Erstellt am 02.12.2025

class RegattaVerwaltung:
    def __init__(self, root):
        self.root = root
        self.root.title("Regatta-Verwaltung (Datenbank)")
        self.root.geometry("1600x900")
        
        # Variablen
        self.db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "regatta_unified.db")
        self.regatten_txt_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Base_Tabs", "Regatten.txt")
        self.selected_regatta_id = None
        self.selected_regatta_data = None
        self.sort_column = None
        self.sort_reverse = False
        
        # Feld-Definitionen aus Regatten.txt
        self.field_definitions = [
            'id_msaccess', 'Datum', 'Datm_neu', 'Regatta', 'Jahr', 'Wasser-Ergo',
            'Original-Reg-Text', 'Strecken', 'Saison', 'Oeffentlich', 'Zeitformat',
            'Zwischenzeiten', 'MasterID', 'EnemyMine', 'use', '2ter_Durchlauf',
            'PDFForm', 'anlegeDatum', 'Bemerkung', 'ER_ME', 'PDF_OCR',
            'RegDatum_ersterTag', 'RegDatum_letzerTag'
        ]
        
        # Datenbank initialisieren
        self.datenbank_initialisieren()
        
        # GUI erstellen
        self.gui_erstellen()
        
        # Daten laden
        self.daten_laden()
    
    def datenbank_initialisieren(self):
        """Erstellt/aktualisiert die Datenbank-Struktur"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Alte Regatta_ Tabelle löschen falls vorhanden
            cursor.execute("DROP TABLE IF EXISTS Regatta_")
            
            # Neue Regatta Tabelle mit korrekter Struktur erstellen
            field_definitions_sql = []
            for field in self.field_definitions:
                if field == 'id_msaccess':
                    field_definitions_sql.append(f"`{field}` INTEGER PRIMARY KEY")
                else:
                    field_definitions_sql.append(f"`{field}` TEXT")
            
            create_sql = f"""
            CREATE TABLE IF NOT EXISTS Regatta (
                {', '.join(field_definitions_sql)}
            )
            """
            
            cursor.execute(create_sql)
            
            # Index für bessere Performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_regatta_jahr ON Regatta(`Jahr`)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_regatta_typ ON Regatta(`Wasser-Ergo`)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_regatta_name ON Regatta(`Regatta`)")
            
            conn.commit()
            conn.close()
            
            print("Datenbank-Struktur erfolgreich erstellt")
            
        except Exception as e:
            messagebox.showerror("Datenbank-Fehler", f"Fehler bei Datenbank-Initialisierung:\\n{str(e)}")
    
    def txt_daten_importieren(self):
        """Importiert Daten aus Regatten.txt in die Datenbank"""
        if not os.path.exists(self.regatten_txt_path):
            messagebox.showerror("Fehler", f"Regatten.txt nicht gefunden:\\n{self.regatten_txt_path}")
            return False
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Tabelle leeren
            cursor.execute("DELETE FROM Regatta")
            
            # Daten aus TXT importieren
            with open(self.regatten_txt_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f, delimiter=';')
                
                # Header überspringen
                header = next(reader)
                header_clean = [field.strip('"') for field in header]
                
                # Daten einfügen
                for row in reader:
                    # Anführungszeichen entfernen
                    clean_row = [field.strip('"') if field else '' for field in row]
                    
                    # SQL INSERT vorbereiten
                    placeholders = ', '.join(['?' for _ in self.field_definitions])
                    insert_sql = f"INSERT INTO Regatta ({', '.join(['`' + f + '`' for f in self.field_definitions])}) VALUES ({placeholders})"
                    
                    # Werte auf Feldlänge anpassen
                    values = []
                    for i, field_name in enumerate(self.field_definitions):
                        if i < len(clean_row):
                            value = clean_row[i]
                        else:
                            value = ''
                        values.append(value)
                    
                    cursor.execute(insert_sql, values)
            
            conn.commit()
            conn.close()
            
            self.status_label.config(text="Daten aus Regatten.txt erfolgreich importiert")
            return True
            
        except Exception as e:
            messagebox.showerror("Import-Fehler", f"Fehler beim Import aus TXT:\\n{str(e)}")
            return False
    
    def gui_erstellen(self):
        """Erstellt die GUI-Elemente"""
        
        # Titel
        titel_frame = tk.Frame(self.root, bg="#34495e", pady=15)
        titel_frame.pack(fill=tk.X)
        
        tk.Label(titel_frame, text="🏁 Regatta-Verwaltung (Datenbank)", 
                 font=("Arial", 18, "bold"), fg="white", bg="#34495e").pack()
        tk.Label(titel_frame, text="Vollständige Verwaltung mit sortierbare Feldern", 
                 font=("Arial", 11), fg="#bdc3c7", bg="#34495e").pack()
        
        # Info über Datenbank
        info_frame = tk.Frame(self.root, bg="#f8f9fa", pady=8)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(info_frame, text="💾 Datenbank:", font=("Arial", 10, "bold"), bg="#f8f9fa").pack(side=tk.LEFT, padx=10)
        self.lbl_db_path = tk.Label(info_frame, text=self.db_path, 
                                   font=("Arial", 9), bg="#f8f9fa", fg="#0066cc")
        self.lbl_db_path.pack(side=tk.LEFT, padx=5)
        
        tk.Label(info_frame, text="📁 TXT-Quelle:", font=("Arial", 10, "bold"), bg="#f8f9fa").pack(side=tk.LEFT, padx=(20, 5))
        self.lbl_txt_path = tk.Label(info_frame, text=self.regatten_txt_path, 
                                    font=("Arial", 9), bg="#f8f9fa", fg="#0066cc")
        self.lbl_txt_path.pack(side=tk.LEFT, padx=5)
        
        # Hauptcontainer
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # Toolbar
        toolbar_frame = tk.Frame(main_frame)
        toolbar_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Buttons erste Reihe
        toolbar1 = tk.Frame(toolbar_frame)
        toolbar1.pack(fill=tk.X, pady=(0, 5))
        
        tk.Button(toolbar1, text="🔄 TXT Import", command=self.txt_import_starten,
                  bg="#e67e22", fg="white", font=("Arial", 10, "bold"), height=2, width=15).pack(side=tk.LEFT, padx=(0, 5))
        
        tk.Button(toolbar1, text="➕ Neue Regatta", command=self.neue_regatta,
                  bg="#27ae60", fg="white", font=("Arial", 10, "bold"), height=2, width=15).pack(side=tk.LEFT, padx=(0, 5))
        
        tk.Button(toolbar1, text="✏️ Bearbeiten", command=self.regatta_bearbeiten,
                  bg="#f39c12", fg="white", font=("Arial", 10, "bold"), height=2, width=15).pack(side=tk.LEFT, padx=(0, 5))
        
        tk.Button(toolbar1, text="🗑️ Löschen", command=self.regatta_loeschen,
                  bg="#e74c3c", fg="white", font=("Arial", 10, "bold"), height=2, width=15).pack(side=tk.LEFT, padx=(0, 5))
        
        tk.Button(toolbar1, text="🔄 Neu laden", command=self.daten_laden,
                  bg="#3498db", fg="white", font=("Arial", 10, "bold"), height=2, width=15).pack(side=tk.LEFT, padx=(0, 5))
        
        # Buttons zweite Reihe
        toolbar2 = tk.Frame(toolbar_frame)
        toolbar2.pack(fill=tk.X)
        
        tk.Button(toolbar2, text="📊 Import starten", command=self.import_starten,
                  bg="#9b59b6", fg="white", font=("Arial", 10, "bold"), height=2, width=15).pack(side=tk.LEFT, padx=(0, 5))
        
        tk.Button(toolbar2, text="💾 TXT Export", command=self.txt_export,
                  bg="#28a745", fg="white", font=("Arial", 10, "bold"), height=2, width=15).pack(side=tk.LEFT, padx=(0, 5))
        
        tk.Button(toolbar2, text="🔍 Suchen", command=self.suchen_dialog,
                  bg="#6c757d", fg="white", font=("Arial", 10, "bold"), height=2, width=15).pack(side=tk.LEFT, padx=(0, 5))
        
        tk.Button(toolbar2, text="📈 Statistik", command=self.statistik_anzeigen,
                  bg="#17a2b8", fg="white", font=("Arial", 10, "bold"), height=2, width=15).pack(side=tk.LEFT, padx=(0, 5))
        
        # Paned Window für geteilte Ansicht
        paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # Linke Seite - Regatta Liste (breiter für alle Spalten)
        left_frame = tk.LabelFrame(paned, text="Regatta-Liste (alle Felder sortierbar)", font=("Arial", 12, "bold"))
        paned.add(left_frame, weight=2)  # Größerer Anteil für die Liste
        
        # Filter-Frame
        filter_frame = tk.Frame(left_frame)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(filter_frame, text="Filter Jahr:", font=("Arial", 9)).pack(side=tk.LEFT)
        self.filter_jahr = ttk.Combobox(filter_frame, width=10, font=("Arial", 9))
        self.filter_jahr.pack(side=tk.LEFT, padx=5)
        self.filter_jahr.bind('<<ComboboxSelected>>', self.filter_anwenden)
        
        tk.Label(filter_frame, text="Typ:", font=("Arial", 9)).pack(side=tk.LEFT, padx=(10, 0))
        self.filter_typ = ttk.Combobox(filter_frame, width=10, font=("Arial", 9))
        self.filter_typ.pack(side=tk.LEFT, padx=5)
        self.filter_typ.bind('<<ComboboxSelected>>', self.filter_anwenden)
        
        tk.Button(filter_frame, text="Alle", command=self.filter_zuruecksetzen,
                  bg="#6c757d", fg="white", font=("Arial", 8)).pack(side=tk.LEFT, padx=5)
        
        # Treeview für Regatten mit ALLEN Spalten
        tree_container = tk.Frame(left_frame)
        tree_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Alle Felder als Spalten
        self.regatta_tree = ttk.Treeview(tree_container, show='headings', height=20)
        self.regatta_tree['columns'] = self.field_definitions
        
        # Spalten konfigurieren - alle sortierbar
        for col in self.field_definitions:
            self.regatta_tree.heading(col, text=col, command=lambda c=col: self.sort_by_column(c))
            
            # Spaltenbreite je nach Feld
            if col == 'id_msaccess':
                self.regatta_tree.column(col, width=60, anchor='center')
            elif col in ['Jahr', 'Saison']:
                self.regatta_tree.column(col, width=70, anchor='center')
            elif col in ['Wasser-Ergo', 'Oeffentlich', 'MasterID', 'EnemyMine']:
                self.regatta_tree.column(col, width=80, anchor='center')
            elif col in ['Datum', 'Datm_neu', 'anlegeDatum']:
                self.regatta_tree.column(col, width=120, anchor='center')
            elif col == 'Regatta':
                self.regatta_tree.column(col, width=200, anchor='w')
            elif col in ['Original-Reg-Text', 'Bemerkung']:
                self.regatta_tree.column(col, width=300, anchor='w')
            else:
                self.regatta_tree.column(col, width=100, anchor='w')
        
        # Scrollbars
        tree_scroll_v = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.regatta_tree.yview)
        tree_scroll_h = ttk.Scrollbar(tree_container, orient=tk.HORIZONTAL, command=self.regatta_tree.xview)
        self.regatta_tree.configure(yscrollcommand=tree_scroll_v.set, xscrollcommand=tree_scroll_h.set)
        
        self.regatta_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll_v.pack(side=tk.RIGHT, fill=tk.Y)
        tree_scroll_h.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Events
        self.regatta_tree.bind('<<TreeviewSelect>>', self.regatta_auswaehlen)
        self.regatta_tree.bind('<Double-1>', self.regatta_doppelklick)
        
        # Rechte Seite - Details
        right_frame = tk.LabelFrame(paned, text="Regatta-Details", font=("Arial", 12, "bold"))
        paned.add(right_frame, weight=1)
        
        # Details Container mit Scrollbar
        details_canvas = tk.Canvas(right_frame)
        details_scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=details_canvas.yview)
        self.scrollable_frame = ttk.Frame(details_canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: details_canvas.configure(scrollregion=details_canvas.bbox("all"))
        )
        
        details_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        details_canvas.configure(yscrollcommand=details_scrollbar.set)
        
        details_canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        details_scrollbar.pack(side="right", fill="y")
        
        # Details Frame
        self.details_frame = self.scrollable_frame
        
        # Initial leeres Details-Frame
        tk.Label(self.details_frame, text="Wählen Sie eine Regatta aus der Liste aus", 
                 font=("Arial", 12), fg="gray").pack(expand=True)
        
        # Statusleiste
        self.status_label = tk.Label(self.root, text="Bereit - Datenbank initialisiert", 
                                     bg="#ecf0f1", anchor=tk.W, font=("Arial", 9))
        self.status_label.pack(fill=tk.X, side=tk.BOTTOM)
    
    def sort_by_column(self, column):
        """Sortiert die Treeview nach der angeklickten Spalte"""
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False
        
        # Daten neu laden mit Sortierung
        self.daten_laden()
        
        # Sortier-Indikator in Spalten-Header
        for col in self.field_definitions:
            if col == column:
                direction = "↓" if self.sort_reverse else "↑"
                self.regatta_tree.heading(col, text=f"{col} {direction}")
            else:
                self.regatta_tree.heading(col, text=col)
    
    def daten_laden(self):
        """Lädt Regatta-Daten aus der Datenbank"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # SQL mit optionaler Sortierung
            sql = "SELECT * FROM Regatta"
            if self.sort_column:
                order_direction = "DESC" if self.sort_reverse else "ASC"
                sql += f" ORDER BY `{self.sort_column}` {order_direction}"
            
            cursor.execute(sql)
            rows = cursor.fetchall()
            conn.close()
            
            # Treeview leeren
            for item in self.regatta_tree.get_children():
                self.regatta_tree.delete(item)
            
            # Daten einfügen
            for row in rows:
                # Werte für Anzeige anpassen
                display_values = []
                for i, value in enumerate(row):
                    str_value = str(value) if value is not None else ''
                    # Lange Texte kürzen
                    field_name = self.field_definitions[i]
                    if field_name in ['Original-Reg-Text', 'Bemerkung'] and len(str_value) > 50:
                        str_value = str_value[:47] + '...'
                    display_values.append(str_value)
                
                # ID als Tag für spätere Referenz
                regatta_id = row[0] if row else None
                self.regatta_tree.insert('', 'end', values=display_values, tags=(regatta_id,))
            
            # Filter-Optionen aktualisieren
            self.filter_optionen_aktualisieren()
            
            anzahl = len(rows)
            self.status_label.config(text=f"{anzahl} Regatten aus Datenbank geladen")
            
        except Exception as e:
            messagebox.showerror("Ladefehler", f"Fehler beim Laden der Daten:\\n{str(e)}")
            self.status_label.config(text="Fehler beim Laden")
    
    def filter_optionen_aktualisieren(self):
        """Aktualisiert Filter-Comboboxen"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Jahre sammeln
            cursor.execute("SELECT DISTINCT Jahr FROM Regatta WHERE Jahr IS NOT NULL AND Jahr != '' ORDER BY Jahr DESC")
            jahre = [row[0] for row in cursor.fetchall()]
            
            # Typen sammeln
            cursor.execute("SELECT DISTINCT [Wasser-Ergo] FROM Regatta WHERE [Wasser-Ergo] IS NOT NULL AND [Wasser-Ergo] != '' ORDER BY [Wasser-Ergo]")
            typen = [row[0] for row in cursor.fetchall()]
            
            conn.close()
            
            # Comboboxen füllen
            self.filter_jahr['values'] = ['Alle'] + jahre
            if self.filter_jahr.get() == '':
                self.filter_jahr.set('Alle')
            
            self.filter_typ['values'] = ['Alle'] + typen
            if self.filter_typ.get() == '':
                self.filter_typ.set('Alle')
                
        except Exception as e:
            print(f"Fehler bei Filter-Update: {e}")
    
    def filter_anwenden(self, event=None):
        """Wendet Filter auf die Daten an"""
        try:
            jahr_filter = self.filter_jahr.get()
            typ_filter = self.filter_typ.get()
            
            # SQL mit Filter
            where_conditions = []
            params = []
            
            if jahr_filter and jahr_filter != 'Alle':
                where_conditions.append("Jahr = ?")
                params.append(jahr_filter)
            
            if typ_filter and typ_filter != 'Alle':
                where_conditions.append("[Wasser-Ergo] = ?")
                params.append(typ_filter)
            
            sql = "SELECT * FROM Regatta"
            if where_conditions:
                sql += " WHERE " + " AND ".join(where_conditions)
            
            if self.sort_column:
                order_direction = "DESC" if self.sort_reverse else "ASC"
                sql += f" ORDER BY `{self.sort_column}` {order_direction}"
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            conn.close()
            
            # Treeview aktualisieren
            for item in self.regatta_tree.get_children():
                self.regatta_tree.delete(item)
            
            for row in rows:
                display_values = []
                for i, value in enumerate(row):
                    str_value = str(value) if value is not None else ''
                    field_name = self.field_definitions[i]
                    if field_name in ['Original-Reg-Text', 'Bemerkung'] and len(str_value) > 50:
                        str_value = str_value[:47] + '...'
                    display_values.append(str_value)
                
                regatta_id = row[0] if row else None
                self.regatta_tree.insert('', 'end', values=display_values, tags=(regatta_id,))
            
            self.status_label.config(text=f"{len(rows)} Regatten gefiltert angezeigt")
            
        except Exception as e:
            messagebox.showerror("Filter-Fehler", f"Fehler beim Filtern:\\n{str(e)}")
    
    def filter_zuruecksetzen(self):
        """Setzt Filter zurück"""
        self.filter_jahr.set('Alle')
        self.filter_typ.set('Alle')
        self.daten_laden()
    
    def regatta_auswaehlen(self, event):
        """Wird aufgerufen wenn eine Regatta ausgewählt wird"""
        selection = self.regatta_tree.selection()
        if not selection:
            return
        
        item = self.regatta_tree.item(selection[0])
        tags = item['tags']
        
        if tags:
            regatta_id = int(tags[0])
            self.selected_regatta_id = regatta_id
            
            # Regatta-Details aus Datenbank laden
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                field_names = '`' + '`, `'.join(self.field_definitions) + '`'
                cursor.execute(f"SELECT {field_names} FROM Regatta WHERE id_msaccess = ?", (regatta_id,))
                row = cursor.fetchone()
                conn.close()
                
                if row:
                    self.selected_regatta_data = dict(zip(self.field_definitions, row))
                    self.details_anzeigen(self.selected_regatta_data)
                
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Laden der Details:\\n{str(e)}")
    
    def details_anzeigen(self, regatta_data):
        """Zeigt Details einer Regatta an"""
        # Alten Inhalt löschen
        for widget in self.details_frame.winfo_children():
            widget.destroy()
        
        # Details-Form erstellen
        regatta_name = regatta_data.get('Regatta', 'Unbekannt')
        tk.Label(self.details_frame, text=f"Regatta: {regatta_name}", 
                 font=("Arial", 14, "bold")).pack(pady=(0, 15))
        
        # Formular Container
        form_frame = tk.Frame(self.details_frame)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        self.form_fields = {}
        
        # Alle Felder anzeigen
        for i, field_name in enumerate(self.field_definitions):
            value = regatta_data.get(field_name, '')
            
            row_frame = tk.Frame(form_frame)
            row_frame.pack(fill=tk.X, pady=2)
            
            # Label
            label_text = field_name.replace('_', ' ').replace('-', ' ')
            label = tk.Label(row_frame, text=f"{label_text}:", width=20, anchor='w', font=("Arial", 9))
            label.pack(side=tk.LEFT)
            
            # Entry Field (ID nicht editierbar)
            if field_name == 'id_msaccess':
                entry = tk.Entry(row_frame, width=50, font=("Arial", 9), state='readonly')
                entry.insert(0, str(value) if value else '')
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
                self.form_fields[field_name] = entry
            elif field_name in ['Original-Reg-Text', 'Bemerkung']:
                # Mehrzeiliges Textfeld
                text_widget = tk.Text(row_frame, height=3, width=50, font=("Arial", 9))
                text_widget.insert('1.0', str(value) if value else '')
                text_widget.pack(side=tk.LEFT, fill=tk.X, expand=True)
                self.form_fields[field_name] = text_widget
            else:
                # Einzeiliges Eingabefeld
                entry = tk.Entry(row_frame, width=50, font=("Arial", 9))
                entry.insert(0, str(value) if value else '')
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
                self.form_fields[field_name] = entry
        
        # Buttons
        button_frame = tk.Frame(self.details_frame)
        button_frame.pack(fill=tk.X, pady=15)
        
        tk.Button(button_frame, text="💾 Änderungen speichern", command=self.regatta_speichern,
                  bg="#27ae60", fg="white", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(button_frame, text="↩️ Zurücksetzen", command=lambda: self.details_anzeigen(self.selected_regatta_data),
                  bg="#95a5a6", fg="white", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
    
    def regatta_speichern(self):
        """Speichert Änderungen an der aktuellen Regatta"""
        if self.selected_regatta_id is None or not hasattr(self, 'form_fields'):
            return
        
        try:
            # Werte aus Formular sammeln
            field_values = []
            for field_name in self.field_definitions:
                if field_name == 'id_msaccess':
                    continue  # ID nicht ändern
                
                widget = self.form_fields.get(field_name)
                if widget:
                    if isinstance(widget, tk.Text):
                        value = widget.get('1.0', tk.END).strip()
                    else:
                        value = widget.get().strip()
                    field_values.append(value)
                else:
                    field_values.append('')
            
            # Update SQL
            field_names = [f for f in self.field_definitions if f != 'id_msaccess']
            set_clause = ', '.join([f'`{f}` = ?' for f in field_names])
            update_sql = f"UPDATE Regatta SET {set_clause} WHERE id_msaccess = ?"
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(update_sql, field_values + [self.selected_regatta_id])
            conn.commit()
            conn.close()
            
            # Daten neu laden
            self.daten_laden()
            
            regatta_name = self.selected_regatta_data.get('Regatta', 'Unbekannt')
            self.status_label.config(text=f"Regatta '{regatta_name}' gespeichert")
            
        except Exception as e:
            messagebox.showerror("Speicher-Fehler", f"Fehler beim Speichern:\\n{str(e)}")
    
    def txt_import_starten(self):
        """Startet Import aus TXT-Datei"""
        antwort = messagebox.askyesno("TXT Import", 
                                     "Möchten Sie alle Daten aus der Regatten.txt importieren?\\n\\n"
                                     "Dies überschreibt alle aktuellen Datenbank-Einträge!")
        if antwort:
            if self.txt_daten_importieren():
                self.daten_laden()
                messagebox.showinfo("Import erfolgreich", "Daten aus Regatten.txt wurden erfolgreich importiert!")
    
    def txt_export(self):
        """Exportiert Daten zurück in TXT-Format"""
        try:
            # Backup der originalen TXT erstellen
            if os.path.exists(self.regatten_txt_path):
                backup_path = f"{self.regatten_txt_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                shutil.copy2(self.regatten_txt_path, backup_path)
            
            # Export-Pfad wählen
            export_path = filedialog.asksaveasfilename(
                title="Export als TXT",
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                initialfile=f"Regatta_Export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            )
            
            if not export_path:
                return
            
            # Daten aus DB exportieren
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            field_names = '`' + '`, `'.join(self.field_definitions) + '`'
            cursor.execute(f"SELECT {field_names} FROM Regatta ORDER BY id_msaccess")
            rows = cursor.fetchall()
            conn.close()
            
            # TXT schreiben
            with open(export_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_ALL)
                
                # Header
                writer.writerow(self.field_definitions)
                
                # Daten
                for row in rows:
                    writer.writerow(row)
            
            self.status_label.config(text=f"Export erstellt: {os.path.basename(export_path)}")
            messagebox.showinfo("Export erfolgreich", f"Daten exportiert nach:\\n{export_path}")
            
        except Exception as e:
            messagebox.showerror("Export-Fehler", f"Fehler beim Export:\\n{str(e)}")
    
    def neue_regatta(self):
        """Erstellt eine neue Regatta"""
        dialog = NeueRegattaDialog(self.root, self.field_definitions)
        result = dialog.result
        
        if result:
            try:
                # Neue ID generieren
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT MAX(id_msaccess) FROM Regatta")
                max_id = cursor.fetchone()[0] or 0
                new_id = max_id + 1
                
                # Insert SQL
                all_fields = ['id_msaccess'] + [f for f in self.field_definitions if f != 'id_msaccess']
                placeholders = ', '.join(['?' for _ in all_fields])
                field_names_sql = '`' + '`, `'.join(all_fields) + '`'
                insert_sql = f"INSERT INTO Regatta ({field_names_sql}) VALUES ({placeholders})"
                
                # Werte vorbereiten
                values = [new_id] + [result.get(f, '') for f in self.field_definitions if f != 'id_msaccess']
                
                cursor.execute(insert_sql, values)
                conn.commit()
                conn.close()
                
                # Daten neu laden
                self.daten_laden()
                
                self.status_label.config(text=f"Neue Regatta '{result.get('Regatta', 'Unbekannt')}' erstellt")
                
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Erstellen der Regatta:\\n{str(e)}")
    
    def regatta_bearbeiten(self):
        """Bearbeitungs-Hinweis"""
        if self.selected_regatta_id is None:
            messagebox.showwarning("Keine Auswahl", "Bitte wählen Sie eine Regatta aus.")
            return
        
        messagebox.showinfo("Bearbeitung", "Verwenden Sie das Details-Panel rechts zum Bearbeiten der Regatta-Daten.")
    
    def regatta_loeschen(self):
        """Löscht die ausgewählte Regatta"""
        if self.selected_regatta_id is None:
            messagebox.showwarning("Keine Auswahl", "Bitte wählen Sie eine Regatta aus.")
            return
        
        regatta_name = self.selected_regatta_data.get('Regatta', 'Unbekannt')
        antwort = messagebox.askyesno("Löschen bestätigen", 
                                     f"Möchten Sie die Regatta '{regatta_name}' wirklich löschen?\\n\\n"
                                     f"Dieser Vorgang kann nicht rückgängig gemacht werden.")
        if not antwort:
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Regatta WHERE id_msaccess = ?", (self.selected_regatta_id,))
            conn.commit()
            conn.close()
            
            # Daten neu laden
            self.daten_laden()
            
            # Details-Frame leeren
            for widget in self.details_frame.winfo_children():
                widget.destroy()
            tk.Label(self.details_frame, text="Wählen Sie eine Regatta aus der Liste aus", 
                     font=("Arial", 12), fg="gray").pack(expand=True)
            
            self.selected_regatta_id = None
            self.selected_regatta_data = None
            self.status_label.config(text=f"Regatta '{regatta_name}' gelöscht")
            
        except Exception as e:
            messagebox.showerror("Lösch-Fehler", f"Fehler beim Löschen:\\n{str(e)}")
    
    def regatta_doppelklick(self, event):
        """Startet Step1_unified_extractor.py mit ausgewählter Regatta"""
        if self.selected_regatta_id is None:
            return
        
        try:
            script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Step1_unified_extractor.py")
            
            if not os.path.exists(script_path):
                messagebox.showerror("Fehler", f"Step1_unified_extractor.py nicht gefunden:\\n{script_path}")
                return
            
            # Regatta-Daten als Umgebungsvariablen setzen
            env = os.environ.copy()
            env['SELECTED_REGATTA_ID'] = str(self.selected_regatta_id)
            env['SELECTED_REGATTA_NAME'] = self.selected_regatta_data.get('Regatta', '')
            
            # Prozess starten
            subprocess.Popen([sys.executable, script_path], 
                           cwd=os.path.dirname(script_path),
                           env=env,
                           creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0)
            
            regatta_name = self.selected_regatta_data.get('Regatta', 'Unbekannt')
            self.status_label.config(text=f"Step1_unified_extractor.py gestartet für: {regatta_name}")
            
        except Exception as e:
            messagebox.showerror("Start-Fehler", f"Fehler beim Starten:\\n{str(e)}")
    
    def import_starten(self):
        """Startet Import-Prozess"""
        if self.selected_regatta_id is None:
            messagebox.showwarning("Keine Auswahl", "Bitte wählen Sie eine Regatta aus.")
            return
        
        self.regatta_doppelklick(None)
    
    def suchen_dialog(self):
        """Öffnet Suchdialog"""
        suchtext = simpledialog.askstring("Suche", "Suchtext eingeben:")
        if not suchtext:
            return
        
        try:
            # Suche in allen Text-Feldern
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Dynamische WHERE-Klauseln für alle Textfelder
            text_fields = [f for f in self.field_definitions if f != 'id_msaccess']
            where_conditions = [f"`{field}` LIKE ?" for field in text_fields]
            where_sql = " OR ".join(where_conditions)
            
            search_pattern = f"%{suchtext}%"
            params = [search_pattern] * len(text_fields)
            
            sql = f"SELECT * FROM Regatta WHERE {where_sql}"
            if self.sort_column:
                order_direction = "DESC" if self.sort_reverse else "ASC"
                sql += f" ORDER BY `{self.sort_column}` {order_direction}"
            
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            conn.close()
            
            # Treeview aktualisieren
            for item in self.regatta_tree.get_children():
                self.regatta_tree.delete(item)
            
            for row in rows:
                display_values = []
                for i, value in enumerate(row):
                    str_value = str(value) if value is not None else ''
                    field_name = self.field_definitions[i]
                    if field_name in ['Original-Reg-Text', 'Bemerkung'] and len(str_value) > 50:
                        str_value = str_value[:47] + '...'
                    display_values.append(str_value)
                
                regatta_id = row[0] if row else None
                self.regatta_tree.insert('', 'end', values=display_values, tags=(regatta_id,))
            
            self.status_label.config(text=f"Suche '{suchtext}': {len(rows)} Treffer")
            
        except Exception as e:
            messagebox.showerror("Such-Fehler", f"Fehler bei der Suche:\\n{str(e)}")
    
    def statistik_anzeigen(self):
        """Zeigt Statistiken an"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Gesamt-Anzahl
            cursor.execute("SELECT COUNT(*) FROM Regatta")
            total = cursor.fetchone()[0]
            
            # Nach Jahr
            cursor.execute("SELECT Jahr, COUNT(*) FROM Regatta WHERE Jahr IS NOT NULL AND Jahr != '' GROUP BY Jahr ORDER BY Jahr DESC")
            jahre_stats = cursor.fetchall()
            
            # Nach Typ
            cursor.execute("SELECT [Wasser-Ergo], COUNT(*) FROM Regatta WHERE [Wasser-Ergo] IS NOT NULL AND [Wasser-Ergo] != '' GROUP BY [Wasser-Ergo] ORDER BY COUNT(*) DESC")
            typ_stats = cursor.fetchall()
            
            conn.close()
            
            # Statistik-Dialog
            stats_window = tk.Toplevel(self.root)
            stats_window.title("Regatta-Statistiken")
            stats_window.geometry("400x500")
            stats_window.transient(self.root)
            
            tk.Label(stats_window, text="📊 Regatta-Statistiken", font=("Arial", 16, "bold")).pack(pady=15)
            
            # Gesamt
            tk.Label(stats_window, text=f"Gesamt: {total} Regatten", font=("Arial", 12, "bold")).pack(pady=5)
            
            # Nach Jahr
            jahr_frame = tk.LabelFrame(stats_window, text="Nach Jahr", font=("Arial", 11, "bold"))
            jahr_frame.pack(fill=tk.X, padx=20, pady=10)
            
            for jahr, anzahl in jahre_stats[:10]:  # Top 10 Jahre
                tk.Label(jahr_frame, text=f"{jahr}: {anzahl}", font=("Arial", 10)).pack(anchor=tk.W, padx=10)
            
            # Nach Typ
            typ_frame = tk.LabelFrame(stats_window, text="Nach Typ", font=("Arial", 11, "bold"))
            typ_frame.pack(fill=tk.X, padx=20, pady=10)
            
            for typ, anzahl in typ_stats:
                tk.Label(typ_frame, text=f"{typ}: {anzahl}", font=("Arial", 10)).pack(anchor=tk.W, padx=10)
            
        except Exception as e:
            messagebox.showerror("Statistik-Fehler", f"Fehler bei Statistik-Erstellung:\\n{str(e)}")


class NeueRegattaDialog:
    """Dialog für neue Regatta"""
    
    def __init__(self, parent, field_definitions):
        self.result = None
        self.field_definitions = field_definitions
        
        # Dialog erstellen
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Neue Regatta erstellen")
        self.dialog.geometry("600x700")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Zentrieren
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (700 // 2)
        self.dialog.geometry(f"600x700+{x}+{y}")
        
        # Formular erstellen
        self.erstelle_formular()
        
        # Modal warten
        self.dialog.wait_window()
    
    def erstelle_formular(self):
        """Erstellt das Eingabeformular"""
        
        # Titel
        tk.Label(self.dialog, text="Neue Regatta erstellen", 
                 font=("Arial", 16, "bold")).pack(pady=15)
        
        # Scrollable Frame
        canvas = tk.Canvas(self.dialog)
        scrollbar = ttk.Scrollbar(self.dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Formular Frame
        form_frame = tk.Frame(scrollable_frame)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.entries = {}
        
        # Felder basierend auf Definition (ID auslassen)
        for i, field_name in enumerate(self.field_definitions):
            if field_name == 'id_msaccess':
                continue  # ID wird automatisch generiert
            
            # Label
            label_text = field_name.replace('_', ' ').replace('-', ' ')
            if field_name in ['Regatta', 'Jahr']:
                label_text += ' *'  # Pflichtfeld
            
            tk.Label(form_frame, text=f"{label_text}:", anchor='w', font=("Arial", 10)).grid(
                row=i, column=0, sticky='w', pady=3, padx=(0, 10))
            
            # Entry
            if field_name in ['Original-Reg-Text', 'Bemerkung']:
                widget = tk.Text(form_frame, height=3, width=40, font=("Arial", 9))
            else:
                widget = tk.Entry(form_frame, width=50, font=("Arial", 9))
                
                # Default-Werte
                if field_name == 'Jahr':
                    widget.insert(0, str(datetime.now().year))
                elif field_name == 'Datm_neu':
                    widget.insert(0, datetime.now().strftime('%d.%m.%Y'))
                elif field_name == 'Wasser-Ergo':
                    widget.insert(0, 'Regatta')
                elif field_name == 'Oeffentlich':
                    widget.insert(0, '1')
                elif field_name == 'Saison':
                    current_year = datetime.now().year
                    if datetime.now().month >= 9:  # Ab September neue Saison
                        season = f"{str(current_year)[2:]}/{str(current_year + 1)[2:]}"
                    else:
                        season = f"{str(current_year - 1)[2:]}/{str(current_year)[2:]}"
                    widget.insert(0, season)
            
            widget.grid(row=i, column=1, sticky='w', pady=3)
            self.entries[field_name] = widget
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Buttons
        button_frame = tk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Button(button_frame, text="💾 Erstellen", command=self.erstellen,
                  bg="#27ae60", fg="white", font=("Arial", 12, "bold"), width=12).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(button_frame, text="❌ Abbrechen", command=self.abbrechen,
                  bg="#e74c3c", fg="white", font=("Arial", 12, "bold"), width=12).pack(side=tk.LEFT)
    
    def erstellen(self):
        """Erstellt die neue Regatta"""
        # Validierung
        regatta_name = self.entries.get('Regatta')
        if regatta_name and hasattr(regatta_name, 'get'):
            name = regatta_name.get().strip()
        else:
            name = ''
        
        if not name:
            messagebox.showerror("Validation", "Regatta Name ist erforderlich!")
            return
        
        # Werte sammeln
        values = {}
        for field_name, widget in self.entries.items():
            if isinstance(widget, tk.Text):
                values[field_name] = widget.get('1.0', tk.END).strip()
            else:
                values[field_name] = widget.get().strip()
        
        self.result = values
        self.dialog.destroy()
    
    def abbrechen(self):
        """Bricht ab ohne zu speichern"""
        self.result = None
        self.dialog.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = RegattaVerwaltung(root)
    root.mainloop()