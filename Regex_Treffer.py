import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
import sqlite3
import re
from datetime import datetime

# Regex-Treffer Extraktor für regatta_unified.db
# Erstellt am 28.11.2025

class RegexTrefferApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Regex-Treffer Extraktor")
        self.root.geometry("800x700")
        
        # Variablen
        self.db_name = "regatta_unified.db"
        self.regex_pattern = r"^[1-4][ \w]*[\.]?[ \w]*\/*[ \w]*([- Boot ]*[1-9]*[ -])*0[1-3]:[0-5][0-9].[0-9][0-9] [1-9][0-9]?"
        self.ausgewaehlte_tabelle = "extracted_data"
        self.ausgewaehltes_feld = "zeile_inhalt"
        
        # GUI Elemente
        # Titel
        titel_label = tk.Label(root, text="Regex-Treffer Extraktor", 
                               font=("Arial", 14, "bold"), bg="#e8f5e8", pady=10)
        titel_label.pack(fill=tk.X)
        
        # Info Frame
        info_frame = tk.Frame(root, bg="#fff3cd", pady=5)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(info_frame, text="🔍 Durchsucht ausgewählte Tabelle nach Regex-Pattern und speichert Treffer", 
                 font=("Arial", 9), bg="#fff3cd").pack()
        
        # Auswahl Frame für Tabelle und Feld
        auswahl_frame = tk.Frame(root, bg="#e9ecef", pady=10)
        auswahl_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Tabellen-Auswahl
        tabelle_frame = tk.Frame(auswahl_frame, bg="#e9ecef")
        tabelle_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(tabelle_frame, text="Quell-Tabelle:", font=("Arial", 10, "bold"), 
                bg="#e9ecef").pack(side=tk.LEFT, padx=(0, 10))
        
        self.combo_tabelle = ttk.Combobox(tabelle_frame, font=("Arial", 10), width=25, state="readonly")
        self.combo_tabelle.pack(side=tk.LEFT, padx=(0, 10))
        self.combo_tabelle.bind("<<ComboboxSelected>>", self.tabelle_geaendert)
        
        btn_refresh_tabellen = tk.Button(tabelle_frame, text="🔄", command=self.tabellen_laden, 
                                        bg="#6c757d", fg="white", font=("Arial", 8))
        btn_refresh_tabellen.pack(side=tk.LEFT)
        
        # Feld-Auswahl
        feld_frame = tk.Frame(auswahl_frame, bg="#e9ecef")
        feld_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(feld_frame, text="Zu durchsuchendes Feld:", font=("Arial", 10, "bold"), 
                bg="#e9ecef").pack(side=tk.LEFT, padx=(0, 10))
        
        self.combo_feld = ttk.Combobox(feld_frame, font=("Arial", 10), width=25, state="readonly")
        self.combo_feld.pack(side=tk.LEFT)
        
        # Regex Pattern Anzeige
        pattern_frame = tk.Frame(root)
        pattern_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(pattern_frame, text="Regex Pattern:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.pattern_text = tk.Text(pattern_frame, height=3, font=("Courier", 9), bg="#f8f9fa")
        self.pattern_text.pack(fill=tk.X, pady=5)
        self.pattern_text.insert(1.0, self.regex_pattern)
        
        # Button: Suche starten
        self.btn_search = tk.Button(root, text="🔍 Suche nach Treffern starten", 
                                    command=self.suche_starten, 
                                    bg="#28a745", fg="white", height=2, 
                                    font=("Arial", 11, "bold"))
        self.btn_search.pack(fill=tk.X, padx=20, pady=10)
        
        # Button: Treffer direkt speichern
        self.btn_search_save = tk.Button(root, text="🔍💾 Suchen und Treffer automatisch speichern", 
                                         command=self.suche_und_speichern, 
                                         bg="#20a744", fg="white", height=2, 
                                         font=("Arial", 11, "bold"))
        self.btn_search_save.pack(fill=tk.X, padx=20, pady=5)
        
        # Statistik Frame
        stats_frame = tk.Frame(root)
        stats_frame.pack(fill=tk.X, padx=20, pady=5)
        
        self.lbl_stats = tk.Label(stats_frame, text="Bereit für Suche", font=("Arial", 10), 
                                  fg="grey", bg="#e9ecef")
        self.lbl_stats.pack(fill=tk.X, pady=5)
        
        # Ergebnis-Anzeige
        tk.Label(root, text="Suchergebnisse:", font=("Arial", 10, "bold")).pack(anchor=tk.W, padx=20, pady=(10,5))
        self.txt_results = scrolledtext.ScrolledText(root, height=20, font=("Courier", 9))
        self.txt_results.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        
        # Button Frame
        btn_frame = tk.Frame(root)
        btn_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Button: Treffer speichern
        self.btn_save = tk.Button(btn_frame, text="💾 Treffer in neue Tabelle speichern", 
                                  command=self.treffer_speichern, 
                                  bg="#ffc107", height=2, state=tk.DISABLED,
                                  font=("Arial", 10, "bold"))
        self.btn_save.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Button: Tabelle anzeigen
        self.btn_show = tk.Button(btn_frame, text="📊 Treffer-Tabelle anzeigen", 
                                  command=self.tabelle_anzeigen, 
                                  bg="#17a2b8", fg="white", height=2,
                                  font=("Arial", 10, "bold"))
        self.btn_show.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Button: Treffer-Tabelle löschen
        self.btn_clear = tk.Button(btn_frame, text="🗑️ Treffer-Tabelle löschen", 
                                   command=self.tabelle_loeschen, 
                                   bg="#dc3545", fg="white", height=2,
                                   font=("Arial", 10, "bold"))
        self.btn_clear.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        # Statusleiste
        self.status_label = tk.Label(root, text="Bereit", bg="#e0e0e0", anchor=tk.W, font=("Arial", 9))
        self.status_label.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Variable für gefundene Treffer
        self.gefundene_treffer = []
        
        # Tabellen beim Start laden
        self.tabellen_laden()
    
    def tabellen_laden(self):
        """Lädt alle verfügbaren Tabellen in die Combobox"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
            tabellen = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            self.combo_tabelle['values'] = tabellen
            
            # Wenn extracted_data vorhanden ist, als Standard setzen
            if 'extracted_data' in tabellen:
                self.combo_tabelle.set('extracted_data')
                self.ausgewaehlte_tabelle = 'extracted_data'
                self.felder_laden()
            elif tabellen:
                self.combo_tabelle.set(tabellen[0])
                self.ausgewaehlte_tabelle = tabellen[0]
                self.felder_laden()
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Laden der Tabellen:\n{str(e)}")
    
    def tabelle_geaendert(self, event=None):
        """Wird aufgerufen wenn eine andere Tabelle ausgewählt wird"""
        self.ausgewaehlte_tabelle = self.combo_tabelle.get()
        self.felder_laden()
    
    def felder_laden(self):
        """Lädt die Felder der ausgewählten Tabelle"""
        if not self.ausgewaehlte_tabelle:
            return
        
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute(f'PRAGMA table_info({self.ausgewaehlte_tabelle})')
            felder_info = cursor.fetchall()
            felder = [info[1] for info in felder_info]
            conn.close()
            
            self.combo_feld['values'] = felder
            
            # Wenn zeile_inhalt vorhanden ist, als Standard setzen
            if 'zeile_inhalt' in felder:
                self.combo_feld.set('zeile_inhalt')
                self.ausgewaehltes_feld = 'zeile_inhalt'
            elif felder:
                self.combo_feld.set(felder[0])
                self.ausgewaehltes_feld = felder[0]
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Laden der Felder:\n{str(e)}")
    
    def suche_starten(self):
        """Startet die Regex-Suche in der extracted_data Tabelle"""
        try:
            # Pattern aus Textfeld holen
            self.regex_pattern = self.pattern_text.get(1.0, tk.END).strip()
            self.ausgewaehlte_tabelle = self.combo_tabelle.get()
            self.ausgewaehltes_feld = self.combo_feld.get()
            
            if not self.regex_pattern:
                messagebox.showerror("Fehler", "Bitte geben Sie ein Regex-Pattern ein!")
                return
            
            if not self.ausgewaehlte_tabelle:
                messagebox.showerror("Fehler", "Bitte wählen Sie eine Tabelle aus!")
                return
            
            if not self.ausgewaehltes_feld:
                messagebox.showerror("Fehler", "Bitte wählen Sie ein Feld aus!")
                return
            
            # Pattern validieren
            try:
                re.compile(self.regex_pattern)
            except re.error as e:
                messagebox.showerror("Ungültiger Regex", f"Das Regex-Pattern ist ungültig:\n{str(e)}")
                return
            
            self.btn_search.config(state=tk.DISABLED)
            self.txt_results.delete(1.0, tk.END)
            self.txt_results.insert(tk.END, "Durchsuche Datenbank...\n\n")
            self.root.update()
            
            # Datenbank-Verbindung
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Prüfen ob Tabelle existiert
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (self.ausgewaehlte_tabelle,))
            if not cursor.fetchone():
                messagebox.showerror("Fehler", f"Tabelle '{self.ausgewaehlte_tabelle}' nicht gefunden!")
                conn.close()
                self.btn_search.config(state=tk.NORMAL)
                return
            
            # Prüfen ob Feld existiert
            cursor.execute(f'PRAGMA table_info({self.ausgewaehlte_tabelle})')
            felder_info = cursor.fetchall()
            verfuegbare_felder = [info[1] for info in felder_info]
            
            if self.ausgewaehltes_feld not in verfuegbare_felder:
                messagebox.showerror("Fehler", f"Feld '{self.ausgewaehltes_feld}' nicht in Tabelle '{self.ausgewaehlte_tabelle}' gefunden!")
                conn.close()
                self.btn_search.config(state=tk.NORMAL)
                return
            
            # Alle Zeilen aus der ausgewählten Tabelle holen
            cursor.execute(f'SELECT id, "{self.ausgewaehltes_feld}" FROM {self.ausgewaehlte_tabelle} WHERE "{self.ausgewaehltes_feld}" IS NOT NULL')
            rows = cursor.fetchall()
            
            conn.close()
            
            if not rows:
                messagebox.showinfo("Keine Daten", f"Keine Daten in Tabelle '{self.ausgewaehlte_tabelle}', Feld '{self.ausgewaehltes_feld}' gefunden!")
                self.btn_search.config(state=tk.NORMAL)
                return
            
            # Regex-Suche durchführen
            self.gefundene_treffer = []
            pattern = re.compile(self.regex_pattern)
            
            for row_id, zeile_inhalt in rows:
                if pattern.match(zeile_inhalt):
                    self.gefundene_treffer.append((row_id, zeile_inhalt))
            
            # Ergebnisse anzeigen
            self.ergebnisse_anzeigen()
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler bei der Suche:\n{str(e)}")
        finally:
            self.btn_search.config(state=tk.NORMAL)
    
    def suche_und_speichern(self):
        """Führt Suche durch und speichert Treffer automatisch"""
        try:
            # Pattern aus Textfeld holen
            self.regex_pattern = self.pattern_text.get(1.0, tk.END).strip()
            self.ausgewaehlte_tabelle = self.combo_tabelle.get()
            self.ausgewaehltes_feld = self.combo_feld.get()
            
            if not self.regex_pattern:
                messagebox.showerror("Fehler", "Bitte geben Sie ein Regex-Pattern ein!")
                return
            
            if not self.ausgewaehlte_tabelle:
                messagebox.showerror("Fehler", "Bitte wählen Sie eine Tabelle aus!")
                return
            
            if not self.ausgewaehltes_feld:
                messagebox.showerror("Fehler", "Bitte wählen Sie ein Feld aus!")
                return
            
            # Pattern validieren
            try:
                re.compile(self.regex_pattern)
            except re.error as e:
                messagebox.showerror("Ungültiger Regex", f"Das Regex-Pattern ist ungültig:\n{str(e)}")
                return
            
            self.btn_search.config(state=tk.DISABLED)
            self.btn_search_save.config(state=tk.DISABLED)
            self.txt_results.delete(1.0, tk.END)
            self.txt_results.insert(tk.END, "Durchsuche Datenbank und speichere Treffer...\n\n")
            self.root.update()
            
            # Datenbank-Verbindung
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Prüfen ob Tabelle existiert
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (self.ausgewaehlte_tabelle,))
            if not cursor.fetchone():
                messagebox.showerror("Fehler", f"Tabelle '{self.ausgewaehlte_tabelle}' nicht gefunden!")
                conn.close()
                return
            
            # Prüfen ob Feld existiert
            cursor.execute(f'PRAGMA table_info({self.ausgewaehlte_tabelle})')
            felder_info = cursor.fetchall()
            verfuegbare_felder = [info[1] for info in felder_info]
            
            if self.ausgewaehltes_feld not in verfuegbare_felder:
                messagebox.showerror("Fehler", f"Feld '{self.ausgewaehltes_feld}' nicht in Tabelle '{self.ausgewaehlte_tabelle}' gefunden!")
                conn.close()
                return
            
            # Alle Zeilen aus der ausgewählten Tabelle holen
            cursor.execute(f'SELECT id, "{self.ausgewaehltes_feld}" FROM {self.ausgewaehlte_tabelle} WHERE "{self.ausgewaehltes_feld}" IS NOT NULL')
            rows = cursor.fetchall()
            
            if not rows:
                messagebox.showinfo("Keine Daten", f"Keine Daten in Tabelle '{self.ausgewaehlte_tabelle}', Feld '{self.ausgewaehltes_feld}' gefunden!")
                conn.close()
                return
            
            # Treffer-Tabelle erstellen (falls nicht vorhanden)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Treffer (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    extracted_data_id INTEGER NOT NULL,
                    zeile_inhalt TEXT NOT NULL,
                    regex_pattern TEXT NOT NULL,
                    quell_tabelle TEXT NOT NULL,
                    quell_feld TEXT NOT NULL,
                    gefunden_am TIMESTAMP NOT NULL
                )
            ''')
            
            # Regex-Suche durchführen und direkt speichern
            pattern = re.compile(self.regex_pattern)
            treffer_count = 0
            
            for row_id, zeile_inhalt in rows:
                if pattern.match(zeile_inhalt):
                    cursor.execute('''
                        INSERT INTO Treffer (extracted_data_id, zeile_inhalt, regex_pattern, quell_tabelle, quell_feld, gefunden_am)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (row_id, zeile_inhalt, self.regex_pattern, self.ausgewaehlte_tabelle, self.ausgewaehltes_feld, datetime.now()))
                    treffer_count += 1
            
            conn.commit()
            conn.close()
            
            # Ergebnis anzeigen
            self.txt_results.delete(1.0, tk.END)
            self.txt_results.insert(tk.END, f"=== SUCHE UND SPEICHERUNG ABGESCHLOSSEN ===\n")
            self.txt_results.insert(tk.END, f"Tabelle: {self.ausgewaehlte_tabelle}\n")
            self.txt_results.insert(tk.END, f"Feld: {self.ausgewaehltes_feld}\n")
            self.txt_results.insert(tk.END, f"Pattern: {self.regex_pattern}\n")
            self.txt_results.insert(tk.END, f"Gefundene Treffer: {treffer_count}\n")
            self.txt_results.insert(tk.END, "="*60 + "\n\n")
            
            if treffer_count > 0:
                self.txt_results.insert(tk.END, f"✅ {treffer_count} Treffer wurden automatisch in der Tabelle 'Treffer' gespeichert!\n")
                messagebox.showinfo("Erfolgreich", f"{treffer_count} Treffer wurden gefunden und gespeichert!")
            else:
                self.txt_results.insert(tk.END, "ℹ️ Keine Treffer gefunden.\n")
                messagebox.showinfo("Keine Treffer", "Keine Treffer für das angegebene Pattern gefunden.")
            
            # Statistik aktualisieren
            self.lbl_stats.config(text=f"Suche abgeschlossen: {treffer_count} Treffer gefunden und gespeichert", 
                                  bg="#d4edda", fg="black")
            self.status_label.config(text=f"Suche abgeschlossen: {treffer_count} Treffer gespeichert")
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler bei Suche und Speicherung:\n{str(e)}")
        finally:
            self.btn_search.config(state=tk.NORMAL)
            self.btn_search_save.config(state=tk.NORMAL)
    
    def ergebnisse_anzeigen(self):
        """Zeigt die gefundenen Treffer an"""
        self.txt_results.delete(1.0, tk.END)
        
        anzahl = len(self.gefundene_treffer)
        
        self.txt_results.insert(tk.END, f"=== SUCHERGEBNISSE ===\n")
        self.txt_results.insert(tk.END, f"Tabelle: {self.ausgewaehlte_tabelle}\n")
        self.txt_results.insert(tk.END, f"Feld: {self.ausgewaehltes_feld}\n")
        self.txt_results.insert(tk.END, f"Pattern: {self.regex_pattern}\n")
        self.txt_results.insert(tk.END, f"Gefunden: {anzahl} Treffer\n")
        self.txt_results.insert(tk.END, "="*60 + "\n\n")
        
        if anzahl == 0:
            self.txt_results.insert(tk.END, "Keine Treffer gefunden.\n")
            self.btn_save.config(state=tk.DISABLED)
        else:
            for i, (row_id, inhalt) in enumerate(self.gefundene_treffer, 1):
                self.txt_results.insert(tk.END, f"Treffer {i} (ID: {row_id}):\n")
                self.txt_results.insert(tk.END, f"  {inhalt}\n")
                self.txt_results.insert(tk.END, "-"*40 + "\n")
            
            self.btn_save.config(state=tk.NORMAL)
        
        # Statistik aktualisieren
        self.lbl_stats.config(text=f"Suche abgeschlossen: {anzahl} Treffer gefunden", 
                              bg="#d4edda", fg="black")
        self.status_label.config(text=f"Suche abgeschlossen: {anzahl} Treffer")
    
    def treffer_speichern(self):
        """Speichert die Treffer in eine neue Tabelle"""
        if not self.gefundene_treffer:
            messagebox.showwarning("Keine Treffer", "Keine Treffer zum Speichern vorhanden!")
            return
        
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Treffer-Tabelle erstellen (falls nicht vorhanden)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Treffer (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    extracted_data_id INTEGER NOT NULL,
                    zeile_inhalt TEXT NOT NULL,
                    regex_pattern TEXT NOT NULL,
                    quell_tabelle TEXT NOT NULL,
                    quell_feld TEXT NOT NULL,
                    gefunden_am TIMESTAMP NOT NULL
                )
            ''')
            
            # Treffer einfügen
            for row_id, inhalt in self.gefundene_treffer:
                cursor.execute('''
                    INSERT INTO Treffer (extracted_data_id, zeile_inhalt, regex_pattern, quell_tabelle, quell_feld, gefunden_am)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (row_id, inhalt, self.regex_pattern, self.ausgewaehlte_tabelle, self.ausgewaehltes_feld, datetime.now()))
            
            conn.commit()
            conn.close()
            
            anzahl = len(self.gefundene_treffer)
            messagebox.showinfo("Erfolgreich gespeichert", 
                               f"{anzahl} Treffer wurden in Tabelle 'Treffer' gespeichert!")
            
            self.status_label.config(text=f"{anzahl} Treffer gespeichert")
            
        except Exception as e:
            messagebox.showerror("Speicherfehler", f"Fehler beim Speichern:\n{str(e)}")
    
    def tabelle_anzeigen(self):
        """Zeigt die Treffer-Tabelle an"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Prüfen ob Tabelle existiert
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Treffer'")
            if not cursor.fetchone():
                messagebox.showinfo("Keine Tabelle", "Tabelle 'Treffer' existiert noch nicht!\nFühren Sie zuerst eine Suche durch und speichern Sie die Treffer.")
                conn.close()
                return
            
            # Treffer abrufen
            cursor.execute('''
                SELECT T.id, T.extracted_data_id, T.zeile_inhalt, T.regex_pattern, T.quell_tabelle, T.quell_feld, T.gefunden_am
                FROM Treffer T
                ORDER BY T.id DESC
            ''')
            treffer = cursor.fetchall()
            
            cursor.execute('SELECT COUNT(*) FROM Treffer')
            anzahl = cursor.fetchone()[0]
            
            conn.close()
            
            # Neues Fenster für Tabelle
            tabelle_window = tk.Toplevel(self.root)
            tabelle_window.title("Treffer-Tabelle")
            tabelle_window.geometry("1200x600")
            
            tk.Label(tabelle_window, text=f"Treffer-Tabelle ({anzahl} Einträge)", 
                    font=("Arial", 12, "bold"), bg="#e8f5e8", pady=10).pack(fill=tk.X)
            
            # Treeview erstellen
            tree_frame = tk.Frame(tabelle_window)
            tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Scrollbars
            vsb = tk.Scrollbar(tree_frame, orient="vertical")
            vsb.pack(side=tk.RIGHT, fill=tk.Y)
            
            hsb = tk.Scrollbar(tree_frame, orient="horizontal")
            hsb.pack(side=tk.BOTTOM, fill=tk.X)
            
            # Treeview
            tree = ttk.Treeview(tree_frame, yscrollcommand=vsb.set, xscrollcommand=hsb.set)
            tree.pack(fill=tk.BOTH, expand=True)
            
            vsb.config(command=tree.yview)
            hsb.config(command=tree.xview)
            
            # Spalten definieren
            spalten = ("ID", "Quell_ID", "Zeile_Inhalt", "Regex_Pattern", "Quell_Tabelle", "Quell_Feld", "Gefunden_am")
            tree["columns"] = spalten
            tree["show"] = "headings"
            
            # Spaltenüberschriften
            for col in spalten:
                tree.heading(col, text=col)
                tree.column(col, width=150, anchor=tk.W)
            
            # Daten einfügen
            for row in treffer:
                tree.insert("", tk.END, values=row)
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Anzeigen der Tabelle:\n{str(e)}")
    
    def tabelle_loeschen(self):
        """Löscht die Treffer-Tabelle"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Prüfen ob Tabelle existiert
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Treffer'")
            if not cursor.fetchone():
                messagebox.showinfo("Keine Tabelle", "Tabelle 'Treffer' existiert nicht!")
                conn.close()
                return
            
            # Anzahl Einträge
            cursor.execute('SELECT COUNT(*) FROM Treffer')
            anzahl = cursor.fetchone()[0]
            
            conn.close()
            
            if anzahl == 0:
                # Tabelle ist leer, einfach löschen
                antwort = messagebox.askyesno("Tabelle löschen?", 
                                             "Die Treffer-Tabelle ist leer.\nMöchten Sie sie trotzdem löschen?")
            else:
                # Bestätigung für gefüllte Tabelle
                antwort = messagebox.askyesno("Tabelle löschen?", 
                                             f"Möchten Sie die Treffer-Tabelle mit {anzahl} Einträgen wirklich löschen?\n\nDiese Aktion kann NICHT rückgängig gemacht werden!",
                                             icon='warning')
            
            if antwort:
                conn = sqlite3.connect(self.db_name)
                cursor = conn.cursor()
                cursor.execute('DROP TABLE Treffer')
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Gelöscht", "Treffer-Tabelle wurde gelöscht!")
                self.status_label.config(text="Treffer-Tabelle gelöscht")
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Löschen:\n{str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = RegexTrefferApp(root)
    root.mainloop()