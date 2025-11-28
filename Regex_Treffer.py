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
        
        # GUI Elemente
        # Titel
        titel_label = tk.Label(root, text="Regex-Treffer Extraktor", 
                               font=("Arial", 14, "bold"), bg="#e8f5e8", pady=10)
        titel_label.pack(fill=tk.X)
        
        # Info Frame
        info_frame = tk.Frame(root, bg="#fff3cd", pady=5)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(info_frame, text="🔍 Durchsucht extracted_data nach Regex-Pattern und speichert Treffer", 
                 font=("Arial", 9), bg="#fff3cd").pack()
        
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
    
    def suche_starten(self):
        """Startet die Regex-Suche in der extracted_data Tabelle"""
        try:
            # Pattern aus Textfeld holen
            self.regex_pattern = self.pattern_text.get(1.0, tk.END).strip()
            
            if not self.regex_pattern:
                messagebox.showerror("Fehler", "Bitte geben Sie ein Regex-Pattern ein!")
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
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='extracted_data'")
            if not cursor.fetchone():
                messagebox.showerror("Fehler", "Tabelle 'extracted_data' nicht gefunden!")
                conn.close()
                self.btn_search.config(state=tk.NORMAL)
                return
            
            # Alle Zeilen aus extracted_data holen
            cursor.execute("SELECT id, zeile_inhalt FROM extracted_data WHERE zeile_inhalt IS NOT NULL")
            rows = cursor.fetchall()
            
            conn.close()
            
            if not rows:
                messagebox.showinfo("Keine Daten", "Keine Daten in extracted_data gefunden!")
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
    
    def ergebnisse_anzeigen(self):
        """Zeigt die gefundenen Treffer an"""
        self.txt_results.delete(1.0, tk.END)
        
        anzahl = len(self.gefundene_treffer)
        
        self.txt_results.insert(tk.END, f"=== SUCHERGEBNISSE ===\n")
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
                    gefunden_am TIMESTAMP NOT NULL,
                    FOREIGN KEY (extracted_data_id) REFERENCES extracted_data (id)
                )
            ''')
            
            # Treffer einfügen
            for row_id, inhalt in self.gefundene_treffer:
                cursor.execute('''
                    INSERT INTO Treffer (extracted_data_id, zeile_inhalt, regex_pattern, gefunden_am)
                    VALUES (?, ?, ?, ?)
                ''', (row_id, inhalt, self.regex_pattern, datetime.now()))
            
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
                SELECT T.id, T.extracted_data_id, T.zeile_inhalt, T.regex_pattern, T.gefunden_am
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
            tabelle_window.geometry("1000x600")
            
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
            spalten = ("ID", "Extracted_ID", "Zeile_Inhalt", "Regex_Pattern", "Gefunden_am")
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