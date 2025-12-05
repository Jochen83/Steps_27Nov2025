import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import os
from datetime import datetime

# Inhalts-Gruppierung und Typisierung Tool
# Erstellt am 05.12.2025

class GruppierungApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Inhalts-Gruppierung und Typisierung")
        self.root.geometry("1000x700")
        
        # Variablen
        self.db_path = "regatta_unified.db"
        self.selected_table = None
        self.selected_field = None
        self.typisierte_tabelle = None
        
        # GUI erstellen
        self.gui_erstellen()
        self.tabellen_laden()
    
    def gui_erstellen(self):
        """Erstellt die GUI-Elemente"""
        
        # Titel
        titel_frame = tk.Frame(self.root, bg="#20c997", pady=15)
        titel_frame.pack(fill=tk.X)
        
        tk.Label(titel_frame, text="📈 Inhalts-Gruppierung und Typisierung", 
                 font=("Arial", 16, "bold"), bg="#20c997", fg="white").pack()
        tk.Label(titel_frame, text="Analyse von Feldinhalten mit Häufigkeitszählung und Typ-Zuordnung", 
                 font=("Arial", 10), bg="#20c997", fg="white").pack()
        
        # Hauptcontainer
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # Oberer Bereich - Auswahl und Steuerung
        control_frame = tk.LabelFrame(main_frame, text="Auswahl und Steuerung", font=("Arial", 12, "bold"))
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Erste Zeile - Tabellenauswahl
        table_frame = tk.Frame(control_frame)
        table_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(table_frame, text="Tabelle:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        
        self.table_combo = ttk.Combobox(table_frame, width=30, state="readonly")
        self.table_combo.pack(side=tk.LEFT, padx=(10, 20))
        self.table_combo.bind('<<ComboboxSelected>>', self.tabelle_ausgewaehlt)
        
        self.btn_refresh_tables = tk.Button(table_frame, text="🔄", command=self.tabellen_laden,
                                           bg="#17a2b8", fg="white", font=("Arial", 9, "bold"))
        self.btn_refresh_tables.pack(side=tk.LEFT, padx=(0, 20))
        
        tk.Label(table_frame, text="Feld:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        
        self.field_combo = ttk.Combobox(table_frame, width=25, state="readonly")
        self.field_combo.pack(side=tk.LEFT, padx=(10, 0))
        
        # Zweite Zeile - Aktionsbuttons
        action_frame = tk.Frame(control_frame)
        action_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.btn_gruppieren = tk.Button(action_frame, text="📊 Gruppierung erstellen", 
                                       command=self.gruppierung_erstellen,
                                       bg="#28a745", fg="white", font=("Arial", 11, "bold"),
                                       height=2, state=tk.DISABLED)
        self.btn_gruppieren.pack(side=tk.LEFT, padx=(0, 10))
        
        self.btn_typisieren = tk.Button(action_frame, text="🏷️ Typisierte Tabelle erstellen", 
                                       command=self.typisierte_tabelle_erstellen,
                                       bg="#fd7e14", fg="white", font=("Arial", 11, "bold"),
                                       height=2, state=tk.DISABLED)
        self.btn_typisieren.pack(side=tk.LEFT, padx=(0, 10))
        
        self.btn_typ_uebertragen = tk.Button(action_frame, text="🔄 Typen übertragen", 
                                            command=self.typen_uebertragen,
                                            bg="#6f42c1", fg="white", font=("Arial", 11, "bold"),
                                            height=2, state=tk.DISABLED)
        self.btn_typ_uebertragen.pack(side=tk.LEFT)
        
        # Mittlerer Bereich - Gruppenergebnisse
        gruppen_frame = tk.LabelFrame(main_frame, text="Gruppenergebnisse (editierbar)", font=("Arial", 12, "bold"))
        gruppen_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Treeview für Gruppenergebnisse
        tree_container = tk.Frame(gruppen_frame)
        tree_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_container, orient="vertical")
        h_scrollbar = ttk.Scrollbar(tree_container, orient="horizontal")
        
        self.gruppen_tree = ttk.Treeview(tree_container, 
                                        columns=("Inhalt", "Typ", "Anzahl"), 
                                        show="headings",
                                        yscrollcommand=v_scrollbar.set,
                                        xscrollcommand=h_scrollbar.set)
        
        v_scrollbar.config(command=self.gruppen_tree.yview)
        h_scrollbar.config(command=self.gruppen_tree.xview)
        
        # Spalten konfigurieren
        self.gruppen_tree.heading("Inhalt", text="Inhalt")
        self.gruppen_tree.heading("Typ", text="Typ (editierbar)")
        self.gruppen_tree.heading("Anzahl", text="Anzahl")
        
        self.gruppen_tree.column("Inhalt", width=400, anchor="w")
        self.gruppen_tree.column("Typ", width=200, anchor="w")
        self.gruppen_tree.column("Anzahl", width=100, anchor="center")
        
        # Grid-Layout für Scrollbars
        self.gruppen_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)
        
        # Doppelklick für Bearbeitung
        self.gruppen_tree.bind('<Double-1>', self.typ_bearbeiten)
        
        # Unterer Bereich - Status und Log
        status_frame = tk.LabelFrame(main_frame, text="Status und Protokoll", font=("Arial", 12, "bold"))
        status_frame.pack(fill=tk.X)
        
        # Statusleiste
        self.status_label = tk.Label(status_frame, text="Bereit", bg="#f8f9fa", anchor=tk.W, 
                                    font=("Arial", 9), relief=tk.SUNKEN)
        self.status_label.pack(fill=tk.X, padx=10, pady=5)
        
        # Log-Bereich
        log_container = tk.Frame(status_frame)
        log_container.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.log_text = tk.Text(log_container, height=6, font=("Courier", 9))
        log_scrollbar = ttk.Scrollbar(log_container, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def log(self, message):
        """Fügt eine Nachricht zum Log hinzu"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def tabellen_laden(self):
        """Lädt alle verfügbaren Tabellen"""
        try:
            if not os.path.exists(self.db_path):
                self.log("❌ Datenbank nicht gefunden")
                return
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            tables = cursor.fetchall()
            
            table_names = [table[0] for table in tables]
            self.table_combo['values'] = table_names
            
            conn.close()
            
            self.log(f"✅ {len(table_names)} Tabellen geladen")
            self.status_label.config(text=f"{len(table_names)} Tabellen verfügbar")
            
        except Exception as e:
            self.log(f"❌ Fehler beim Laden der Tabellen: {str(e)}")
            messagebox.showerror("Fehler", f"Fehler beim Laden der Tabellen:\n{str(e)}")
    
    def tabelle_ausgewaehlt(self, event):
        """Wird aufgerufen wenn eine Tabelle ausgewählt wird"""
        self.selected_table = self.table_combo.get()
        if not self.selected_table:
            return
        
        try:
            # Felder der Tabelle laden
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(f"PRAGMA table_info(`{self.selected_table}`)")
            columns = cursor.fetchall()
            
            field_names = [col[1] for col in columns]
            self.field_combo['values'] = field_names
            self.field_combo.set('')  # Auswahl zurücksetzen
            
            conn.close()
            
            self.log(f"📋 Tabelle '{self.selected_table}' ausgewählt - {len(field_names)} Felder verfügbar")
            self.status_label.config(text=f"Tabelle: {self.selected_table} ({len(field_names)} Felder)")
            
            # Buttons zurücksetzen
            self.btn_gruppieren.config(state=tk.DISABLED)
            self.selected_field = None
            
        except Exception as e:
            self.log(f"❌ Fehler beim Laden der Felder: {str(e)}")
            messagebox.showerror("Fehler", f"Fehler beim Laden der Felder:\n{str(e)}")
    
    def gruppierung_erstellen(self):
        """Erstellt die Gruppierung basierend auf dem ausgewählten Feld"""
        self.selected_field = self.field_combo.get()
        
        if not self.selected_table or not self.selected_field:
            messagebox.showwarning("Incomplete Selection", "Bitte wählen Sie Tabelle und Feld aus.")
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Gruppen_Anzahl Tabelle erstellen/leeren
            cursor.execute("DROP TABLE IF EXISTS Gruppen_Anzahl")
            cursor.execute("""
                CREATE TABLE Gruppen_Anzahl (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Inhalt TEXT,
                    Typ TEXT,
                    Anzahl INTEGER
                )
            """)
            
            # Gruppierung durchführen
            cursor.execute(f"""
                SELECT `{self.selected_field}`, COUNT(*) as anzahl 
                FROM `{self.selected_table}` 
                WHERE `{self.selected_field}` IS NOT NULL 
                GROUP BY `{self.selected_field}` 
                ORDER BY anzahl DESC
            """)
            
            ergebnisse = cursor.fetchall()
            
            # Ergebnisse in Gruppen_Anzahl speichern
            for inhalt, anzahl in ergebnisse:
                cursor.execute("""
                    INSERT INTO Gruppen_Anzahl (Inhalt, Typ, Anzahl)
                    VALUES (?, '', ?)
                """, (str(inhalt), anzahl))
            
            conn.commit()
            conn.close()
            
            # Ergebnisse in TreeView anzeigen
            self.gruppenergebnisse_anzeigen()
            
            # Buttons aktivieren
            self.btn_typisieren.config(state=tk.NORMAL)
            
            self.log(f"📊 Gruppierung erstellt: {len(ergebnisse)} eindeutige Werte in '{self.selected_field}'")
            self.status_label.config(text=f"Gruppierung erstellt: {len(ergebnisse)} Gruppen")
            
        except Exception as e:
            self.log(f"❌ Fehler beim Erstellen der Gruppierung: {str(e)}")
            messagebox.showerror("Fehler", f"Fehler beim Erstellen der Gruppierung:\n{str(e)}")
    
    def gruppenergebnisse_anzeigen(self):
        """Zeigt die Gruppenergebnisse im TreeView an"""
        try:
            # TreeView leeren
            for item in self.gruppen_tree.get_children():
                self.gruppen_tree.delete(item)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT Inhalt, Typ, Anzahl FROM Gruppen_Anzahl ORDER BY Anzahl DESC")
            ergebnisse = cursor.fetchall()
            
            for inhalt, typ, anzahl in ergebnisse:
                self.gruppen_tree.insert("", "end", values=(inhalt, typ, anzahl))
            
            conn.close()
            
        except Exception as e:
            self.log(f"❌ Fehler beim Anzeigen der Ergebnisse: {str(e)}")
    
    def typ_bearbeiten(self, event):
        """Ermöglicht die Bearbeitung des Typ-Feldes"""
        item = self.gruppen_tree.selection()[0]
        column = self.gruppen_tree.identify_column(event.x)
        
        # Nur Typ-Spalte (Spalte #2) ist editierbar
        if column == '#2':
            x, y, width, height = self.gruppen_tree.bbox(item, column)
            
            # Entry-Widget für Bearbeitung
            entry = tk.Entry(self.gruppen_tree)
            entry.place(x=x, y=y, width=width, height=height)
            
            # Aktuellen Wert setzen
            current_value = self.gruppen_tree.item(item, 'values')[1]
            entry.insert(0, current_value)
            entry.focus()
            
            def save_edit(event=None):
                new_value = entry.get()
                values = list(self.gruppen_tree.item(item, 'values'))
                values[1] = new_value
                self.gruppen_tree.item(item, values=values)
                
                # In Datenbank speichern
                self.typ_in_db_speichern(values[0], new_value)
                entry.destroy()
            
            def cancel_edit(event=None):
                entry.destroy()
            
            entry.bind('<Return>', save_edit)
            entry.bind('<Escape>', cancel_edit)
            entry.bind('<FocusOut>', save_edit)
    
    def typ_in_db_speichern(self, inhalt, typ):
        """Speichert den Typ in der Datenbank"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("UPDATE Gruppen_Anzahl SET Typ = ? WHERE Inhalt = ?", (typ, inhalt))
            conn.commit()
            conn.close()
            
            self.log(f"💾 Typ '{typ}' für Inhalt '{inhalt}' gespeichert")
            
        except Exception as e:
            self.log(f"❌ Fehler beim Speichern des Typs: {str(e)}")
    
    def typisierte_tabelle_erstellen(self):
        """Erstellt eine typisierte Kopie der ursprünglichen Tabelle"""
        if not self.selected_table:
            messagebox.showwarning("Keine Tabelle", "Bitte wählen Sie eine Tabelle aus.")
            return
        
        try:
            self.typisierte_tabelle = f"{self.selected_table}_Typisiert"
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Alte typisierte Tabelle löschen falls vorhanden
            cursor.execute(f"DROP TABLE IF EXISTS `{self.typisierte_tabelle}`")
            
            # Ursprungstabelle kopieren
            cursor.execute(f"CREATE TABLE `{self.typisierte_tabelle}` AS SELECT * FROM `{self.selected_table}`")
            
            # Typ-Spalte hinzufügen
            cursor.execute(f"ALTER TABLE `{self.typisierte_tabelle}` ADD COLUMN Typ TEXT")
            
            conn.commit()
            conn.close()
            
            # Button aktivieren
            self.btn_typ_uebertragen.config(state=tk.NORMAL)
            
            self.log(f"🏷️ Typisierte Tabelle '{self.typisierte_tabelle}' erstellt")
            self.status_label.config(text=f"Typisierte Tabelle: {self.typisierte_tabelle}")
            
            messagebox.showinfo("Erfolg", f"Typisierte Tabelle '{self.typisierte_tabelle}' wurde erstellt.")
            
        except Exception as e:
            self.log(f"❌ Fehler beim Erstellen der typisierten Tabelle: {str(e)}")
            messagebox.showerror("Fehler", f"Fehler beim Erstellen der typisierten Tabelle:\n{str(e)}")
    
    def typen_uebertragen(self):
        """Überträgt die Typen auf die typisierte Tabelle"""
        if not self.typisierte_tabelle or not self.selected_field:
            messagebox.showwarning("Unvollständig", "Erst Gruppierung und typisierte Tabelle erstellen.")
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Typ-Mappings aus Gruppen_Anzahl holen
            cursor.execute("SELECT Inhalt, Typ FROM Gruppen_Anzahl WHERE Typ != ''")
            typ_mappings = cursor.fetchall()
            
            if not typ_mappings:
                messagebox.showwarning("Keine Typen", "Bitte definieren Sie erst Typen in der Gruppierung.")
                conn.close()
                return
            
            # Typen übertragen
            uebertragene_zeilen = 0
            for inhalt, typ in typ_mappings:
                cursor.execute(f"""
                    UPDATE `{self.typisierte_tabelle}` 
                    SET Typ = ? 
                    WHERE `{self.selected_field}` = ?
                """, (typ, inhalt))
                
                uebertragene_zeilen += cursor.rowcount
            
            conn.commit()
            conn.close()
            
            self.log(f"🔄 {len(typ_mappings)} Typen auf {uebertragene_zeilen} Zeilen übertragen")
            self.status_label.config(text=f"Typen übertragen: {uebertragene_zeilen} Zeilen aktualisiert")
            
            messagebox.showinfo("Erfolg", 
                               f"Typen erfolgreich übertragen!\n\n"
                               f"{len(typ_mappings)} verschiedene Typen\n"
                               f"{uebertragene_zeilen} Zeilen aktualisiert\n\n"
                               f"Tabelle: {self.typisierte_tabelle}")
            
        except Exception as e:
            self.log(f"❌ Fehler beim Übertragen der Typen: {str(e)}")
            messagebox.showerror("Fehler", f"Fehler beim Übertragen der Typen:\n{str(e)}")
    
    # Event-Handler für Feldauswahl
    def on_field_selected(self, event=None):
        """Aktiviert Gruppierung-Button wenn Feld ausgewählt ist"""
        if self.field_combo.get():
            self.btn_gruppieren.config(state=tk.NORMAL)
        else:
            self.btn_gruppieren.config(state=tk.DISABLED)


if __name__ == "__main__":
    root = tk.Tk()
    app = GruppierungApp(root)
    
    # Event-Binding für Feldauswahl
    app.field_combo.bind('<<ComboboxSelected>>', app.on_field_selected)
    
    root.mainloop()