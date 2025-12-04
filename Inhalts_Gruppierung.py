import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import os
from datetime import datetime

# Inhalts-Gruppierung Tool für regatta_unified.db
# Erstellt am 30.11.2025

class InhaltsGruppierungApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Inhalts-Gruppierung Tool")
        self.root.geometry("1000x800")
        
        # Variablen
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_name = os.path.join(script_dir, "regatta_unified.db")
        
        # GUI erstellen
        self.gui_erstellen()
        
        # Tabellen beim Start laden
        self.tabellen_laden()
        
        # Datenbank-Schema initialisieren
        self.init_database_schema()
    
    def gui_erstellen(self):
        """Erstellt die GUI-Elemente"""
        
        # Titel
        titel_label = tk.Label(self.root, text="Inhalts-Gruppierung Tool", 
                               font=("Arial", 16, "bold"), bg="#e8f5e8", pady=15)
        titel_label.pack(fill=tk.X)
        
        # Info Frame
        info_frame = tk.Frame(self.root, bg="#fff3cd", pady=10)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(info_frame, text="📊 Gruppiert Inhalte nach Häufigkeit und ermöglicht Typ-Zuordnung", 
                 font=("Arial", 10), bg="#fff3cd").pack()
        
        # Hauptcontainer
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Tabellen-Auswahl Frame
        auswahl_frame = tk.LabelFrame(main_frame, text="Quell-Tabelle auswählen", 
                                      font=("Arial", 12, "bold"), pady=10)
        auswahl_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Tabelle Auswahl
        tk.Label(auswahl_frame, text="Tabelle:", font=("Arial", 10, "bold")).grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.combo_tabelle = ttk.Combobox(auswahl_frame, font=("Arial", 10), 
                                          width=30, state="readonly")
        self.combo_tabelle.grid(row=0, column=1, padx=5, pady=5)
        self.combo_tabelle.bind("<<ComboboxSelected>>", self.tabelle_geaendert)
        
        # Inhalt Feld
        tk.Label(auswahl_frame, text="Inhalt Feld:", font=("Arial", 10, "bold")).grid(
            row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.combo_inhalt_feld = ttk.Combobox(auswahl_frame, font=("Arial", 10), 
                                              width=20, state="readonly")
        self.combo_inhalt_feld.grid(row=0, column=3, padx=5, pady=5)
        
        # Typ Feld
        tk.Label(auswahl_frame, text="Typ Feld:", font=("Arial", 10, "bold")).grid(
            row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.combo_typ_feld = ttk.Combobox(auswahl_frame, font=("Arial", 10), 
                                           width=20, state="readonly")
        self.combo_typ_feld.grid(row=1, column=1, padx=5, pady=5)
        
        # Button Frame
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        # Gruppierung erstellen Button
        self.btn_gruppieren = tk.Button(button_frame, text="📊 Gruppierung erstellen", 
                                        command=self.gruppierung_erstellen,
                                        bg="#28a745", fg="white", height=2, width=20,
                                        font=("Arial", 11, "bold"))
        self.btn_gruppieren.pack(side=tk.LEFT, padx=(0, 10))
        
        # Typen übertragen Button
        self.btn_uebertragen = tk.Button(button_frame, text="🔄 Typen übertragen", 
                                        command=self.typen_uebertragen,
                                        bg="#17a2b8", fg="white", height=2, width=20,
                                        font=("Arial", 11, "bold"))
        self.btn_uebertragen.pack(side=tk.LEFT, padx=(0, 10))
        
        # Gruppierung löschen Button
        self.btn_loeschen = tk.Button(button_frame, text="🗑️ Gruppierung löschen", 
                                     command=self.gruppierung_loeschen,
                                     bg="#dc3545", fg="white", height=2, width=20,
                                     font=("Arial", 11, "bold"))
        self.btn_loeschen.pack(side=tk.LEFT)
        
        # Statistik Frame
        stats_frame = tk.Frame(main_frame)
        stats_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.lbl_stats = tk.Label(stats_frame, text="Bereit für Gruppierung", 
                                  font=("Arial", 10), fg="grey", bg="#e9ecef")
        self.lbl_stats.pack(fill=tk.X, pady=5)
        
        # Treeview Frame
        tree_frame = tk.LabelFrame(main_frame, text="Gruppierte Inhalte (editierbar)", 
                                   font=("Arial", 12, "bold"))
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Scrollbars
        v_scrollbar = tk.Scrollbar(tree_frame, orient="vertical")
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        h_scrollbar = tk.Scrollbar(tree_frame, orient="horizontal")
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Treeview
        self.tree = ttk.Treeview(tree_frame, 
                                yscrollcommand=v_scrollbar.set, 
                                xscrollcommand=h_scrollbar.set)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        v_scrollbar.config(command=self.tree.yview)
        h_scrollbar.config(command=self.tree.xview)
        
        # Spalten definieren
        self.tree["columns"] = ("ID", "Inhalt", "Typ", "Anzahl")
        self.tree["show"] = "headings"
        
        # Spaltenüberschriften
        self.tree.heading("ID", text="ID")
        self.tree.heading("Inhalt", text="Inhalt")
        self.tree.heading("Typ", text="Typ")
        self.tree.heading("Anzahl", text="Anzahl")
        
        # Spaltenbreiten
        self.tree.column("ID", width=60, anchor=tk.W)
        self.tree.column("Inhalt", width=400, anchor=tk.W)
        self.tree.column("Typ", width=150, anchor=tk.W)
        self.tree.column("Anzahl", width=80, anchor=tk.CENTER)
        
        # Doppelklick für Bearbeitung
        self.tree.bind("<Double-1>", self.zeile_bearbeiten)
        
        # Statusleiste
        self.status_label = tk.Label(self.root, text="Bereit", bg="#e0e0e0", 
                                     anchor=tk.W, font=("Arial", 9))
        self.status_label.pack(fill=tk.X, side=tk.BOTTOM)
    
    def init_database_schema(self):
        """Initialisiert das Datenbank-Schema für GrupInhalt"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # GrupInhalt Tabelle erstellen
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS GrupInhalt (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Inhalt TEXT NOT NULL UNIQUE,
                    Typ TEXT,
                    Anzahl INTEGER NOT NULL DEFAULT 0,
                    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Fehler bei Schema-Initialisierung: {e}")
    
    def tabellen_laden(self):
        """Lädt alle verfügbaren Tabellen"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
            tabellen = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            self.combo_tabelle['values'] = tabellen
            
            # Standard-Werte setzen
            if any('GA_ER_2023' in t for t in tabellen):
                ga_table = next(t for t in tabellen if 'GA_ER_2023' in t)
                self.combo_tabelle.set(ga_table)
                self.felder_laden()
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Laden der Tabellen:\n{str(e)}")
    
    def tabelle_geaendert(self, event=None):
        """Wird aufgerufen wenn Tabelle geändert wird"""
        self.felder_laden()
    
    def felder_laden(self):
        """Lädt die Felder der ausgewählten Tabelle"""
        tabelle = self.combo_tabelle.get()
        if not tabelle:
            return
        
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute(f'PRAGMA table_info({tabelle})')
            felder_info = cursor.fetchall()
            felder = [info[1] for info in felder_info]
            conn.close()
            
            self.combo_inhalt_feld['values'] = felder
            self.combo_typ_feld['values'] = felder
            
            # Standard-Werte setzen
            if 'Inhalt' in felder:
                self.combo_inhalt_feld.set('Inhalt')
            if 'Typ' in felder:
                self.combo_typ_feld.set('Typ')
                
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Laden der Felder:\n{str(e)}")
    
    def gruppierung_erstellen(self):
        """Erstellt die Gruppierung der Inhalte"""
        tabelle = self.combo_tabelle.get()
        inhalt_feld = self.combo_inhalt_feld.get()
        
        if not tabelle or not inhalt_feld:
            messagebox.showerror("Fehler", "Bitte wählen Sie Tabelle und Inhalt-Feld aus!")
            return
        
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # GrupInhalt Tabelle leeren
            cursor.execute("DELETE FROM GrupInhalt")
            
            # Gruppierung erstellen
            cursor.execute(f'''
                INSERT INTO GrupInhalt (Inhalt, Anzahl)
                SELECT "{inhalt_feld}", COUNT(*) as anzahl
                FROM {tabelle}
                WHERE "{inhalt_feld}" IS NOT NULL AND "{inhalt_feld}" != ''
                AND "Typ" = 'PDF'
                GROUP BY "{inhalt_feld}"
                ORDER BY anzahl DESC
            ''')
            
            # Statistik abrufen
            cursor.execute("SELECT COUNT(*), SUM(Anzahl) FROM GrupInhalt")
            gruppen_anzahl, gesamt_zeilen = cursor.fetchone()
            
            conn.commit()
            conn.close()
            
            # GUI aktualisieren
            self.gruppierung_anzeigen()
            
            self.lbl_stats.config(text=f"Gruppierung erstellt: {gruppen_anzahl} Gruppen, {gesamt_zeilen} Zeilen", 
                                  bg="#d4edda", fg="black")
            self.status_label.config(text=f"Gruppierung: {gruppen_anzahl} Gruppen erstellt")
            
            messagebox.showinfo("Erfolgreich", 
                               f"Gruppierung erstellt!\n\nGruppen: {gruppen_anzahl}\nZeilen: {gesamt_zeilen}")
            
        except Exception as e:
            messagebox.showerror("Gruppierungs-Fehler", f"Fehler bei der Gruppierung:\n{str(e)}")
    
    def gruppierung_anzeigen(self):
        """Zeigt die Gruppierung im Treeview an"""
        try:
            # Treeview leeren
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Gruppierte Daten laden (absteigend nach Anzahl)
            cursor.execute('''
                SELECT id, Inhalt, Typ, Anzahl 
                FROM GrupInhalt 
                ORDER BY Anzahl DESC, Inhalt ASC
            ''')
            daten = cursor.fetchall()
            conn.close()
            
            # Daten in Treeview einfügen
            for row in daten:
                id_val, inhalt, typ, anzahl = row
                # Lange Inhalte kürzen für bessere Anzeige
                if inhalt and len(str(inhalt)) > 80:
                    inhalt_display = str(inhalt)[:77] + "..."
                else:
                    inhalt_display = inhalt
                
                typ_display = typ if typ else ""
                
                self.tree.insert("", tk.END, values=(id_val, inhalt_display, typ_display, anzahl))
            
        except Exception as e:
            messagebox.showerror("Anzeige-Fehler", f"Fehler beim Anzeigen der Gruppierung:\n{str(e)}")
    
    def zeile_bearbeiten(self, event):
        """Bearbeitet das Typ-Feld einer Zeile"""
        try:
            item = self.tree.selection()[0]
            values = self.tree.item(item, 'values')
            
            if not values:
                return
            
            id_val, inhalt, typ_alt, anzahl = values
            
            # Bearbeitung-Dialog
            dialog = tk.Toplevel(self.root)
            dialog.title("Typ bearbeiten")
            dialog.geometry("400x200")
            dialog.transient(self.root)
            dialog.grab_set()
            
            # Position zentrieren
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
            y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
            dialog.geometry(f"+{x}+{y}")
            
            # Inhalt anzeigen
            tk.Label(dialog, text="Inhalt:", font=("Arial", 10, "bold")).pack(anchor=tk.W, padx=10, pady=5)
            inhalt_label = tk.Label(dialog, text=str(inhalt), font=("Arial", 9), 
                                   bg="#f8f9fa", relief=tk.SUNKEN)
            inhalt_label.pack(fill=tk.X, padx=10, pady=(0, 10))
            
            tk.Label(dialog, text=f"Anzahl: {anzahl}", font=("Arial", 9)).pack(anchor=tk.W, padx=10)
            
            # Typ eingeben
            tk.Label(dialog, text="Typ:", font=("Arial", 10, "bold")).pack(anchor=tk.W, padx=10, pady=(10, 5))
            typ_entry = tk.Entry(dialog, font=("Arial", 10), width=40)
            typ_entry.pack(fill=tk.X, padx=10, pady=(0, 10))
            typ_entry.insert(0, typ_alt if typ_alt else "")
            typ_entry.focus()
            typ_entry.select_range(0, tk.END)
            
            # Button Frame
            btn_frame = tk.Frame(dialog)
            btn_frame.pack(fill=tk.X, padx=10, pady=10)
            
            def speichern():
                neuer_typ = typ_entry.get().strip()
                self.typ_speichern(id_val, neuer_typ, item)
                dialog.destroy()
            
            def abbrechen():
                dialog.destroy()
            
            tk.Button(btn_frame, text="💾 Speichern", command=speichern,
                     bg="#28a745", fg="white", font=("Arial", 10)).pack(side=tk.LEFT, padx=(0, 5))
            tk.Button(btn_frame, text="❌ Abbrechen", command=abbrechen,
                     bg="#6c757d", fg="white", font=("Arial", 10)).pack(side=tk.LEFT)
            
            # Enter zum Speichern
            dialog.bind('<Return>', lambda e: speichern())
            dialog.bind('<Escape>', lambda e: abbrechen())
            
        except IndexError:
            pass  # Keine Auswahl
        except Exception as e:
            messagebox.showerror("Bearbeitungs-Fehler", f"Fehler beim Bearbeiten:\n{str(e)}")
    
    def typ_speichern(self, id_val, neuer_typ, tree_item):
        """Speichert den neuen Typ in der Datenbank"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Typ aktualisieren
            cursor.execute("UPDATE GrupInhalt SET Typ = ? WHERE id = ?", 
                          (neuer_typ if neuer_typ else None, id_val))
            conn.commit()
            conn.close()
            
            # Treeview aktualisieren
            values = list(self.tree.item(tree_item, 'values'))
            values[2] = neuer_typ  # Typ-Spalte
            self.tree.item(tree_item, values=values)
            
            self.status_label.config(text=f"Typ aktualisiert: ID {id_val}")
            
        except Exception as e:
            messagebox.showerror("Speicher-Fehler", f"Fehler beim Speichern:\n{str(e)}")
    
    def typen_uebertragen(self):
        """Überträgt Typen von GrupInhalt zur Quell-Tabelle"""
        tabelle = self.combo_tabelle.get()
        inhalt_feld = self.combo_inhalt_feld.get()
        typ_feld = self.combo_typ_feld.get()
        
        if not tabelle or not inhalt_feld or not typ_feld:
            messagebox.showerror("Fehler", "Bitte wählen Sie alle Felder aus!")
            return
        
        # Bestätigung
        antwort = messagebox.askyesno("Typen übertragen?", 
                                     f"Möchten Sie die Typen von GrupInhalt\nzur Tabelle '{tabelle}' übertragen?\n\nFeld: {typ_feld}")
        if not antwort:
            return
        
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Nicht-leere Typen aus GrupInhalt holen
            cursor.execute('''
                SELECT Inhalt, Typ 
                FROM GrupInhalt 
                WHERE Typ IS NOT NULL AND Typ != ''
            ''')
            typ_mappings = cursor.fetchall()
            
            if not typ_mappings:
                messagebox.showinfo("Keine Typen", "Keine Typen zum Übertragen gefunden!")
                conn.close()
                return
            
            # Typen übertragen
            uebertragen_count = 0
            for inhalt, typ in typ_mappings:
                cursor.execute(f'''
                    UPDATE {tabelle} 
                    SET "{typ_feld}" = ? 
                    WHERE "{inhalt_feld}" = ?
                ''', (typ, inhalt))
                uebertragen_count += cursor.rowcount
            
            conn.commit()
            conn.close()
            
            self.lbl_stats.config(text=f"Übertragung abgeschlossen: {len(typ_mappings)} Typen, {uebertragen_count} Zeilen aktualisiert", 
                                  bg="#d4edda", fg="black")
            self.status_label.config(text=f"Übertragen: {uebertragen_count} Zeilen aktualisiert")
            
            messagebox.showinfo("Übertragung erfolgreich", 
                               f"Typen wurden übertragen!\n\nTyp-Mappings: {len(typ_mappings)}\nAktualisierte Zeilen: {uebertragen_count}")
            
        except Exception as e:
            messagebox.showerror("Übertragungs-Fehler", f"Fehler bei der Übertragung:\n{str(e)}")
    
    def gruppierung_loeschen(self):
        """Löscht die GrupInhalt Tabelle"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM GrupInhalt")
            anzahl = cursor.fetchone()[0]
            
            if anzahl == 0:
                messagebox.showinfo("Keine Daten", "GrupInhalt Tabelle ist bereits leer!")
                conn.close()
                return
            
            antwort = messagebox.askyesno("Gruppierung löschen?", 
                                         f"Möchten Sie die Gruppierung mit {anzahl} Einträgen löschen?\n\nDiese Aktion kann NICHT rückgängig gemacht werden!",
                                         icon='warning')
            
            if antwort:
                cursor.execute("DELETE FROM GrupInhalt")
                conn.commit()
                conn.close()
                
                # Treeview leeren
                for item in self.tree.get_children():
                    self.tree.delete(item)
                
                self.lbl_stats.config(text="Gruppierung gelöscht", bg="#f8d7da", fg="black")
                self.status_label.config(text="Gruppierung gelöscht")
                
                messagebox.showinfo("Gelöscht", "Gruppierung wurde gelöscht!")
            else:
                conn.close()
            
        except Exception as e:
            messagebox.showerror("Lösch-Fehler", f"Fehler beim Löschen:\n{str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = InhaltsGruppierungApp(root)
    root.mainloop()