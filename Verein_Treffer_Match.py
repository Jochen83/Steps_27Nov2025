import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
import sqlite3
from datetime import datetime
import re
import os

# Verein-Treffer Matcher für regatta_unified.db
# Erstellt am 28.11.2025

class VereinTrefferApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Verein-Treffer Abgleich")
        self.root.geometry("900x800")
        
        # Variablen
        # Absoluter Pfad zur Datenbank (im gleichen Verzeichnis wie das Skript)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_name = os.path.join(script_dir, "regatta_unified.db")
        
        # GUI Elemente
        # Titel
        titel_label = tk.Label(root, text="Verein-Treffer Abgleich", 
                               font=("Arial", 14, "bold"), bg="#e8f5e8", pady=10)
        titel_label.pack(fill=tk.X)
        
        # Info Frame
        info_frame = tk.Frame(root, bg="#fff3cd", pady=10)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(info_frame, text="🏁 Gleicht Treffer-Zeilen mit Vereinsnamen ab", 
                 font=("Arial", 10), bg="#fff3cd").pack()
        tk.Label(info_frame, text="Erstellt Tabelle 'Treffer_Verein_Hit' mit gefundenen Vereinen", 
                 font=("Arial", 9), bg="#fff3cd", fg="grey").pack()
        
        # Statistik Frame
        stats_frame = tk.Frame(root, bg="#e9ecef", pady=10)
        stats_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.lbl_stats_treffer = tk.Label(stats_frame, text="Treffer-Tabelle: Noch nicht geprüft", 
                                         font=("Arial", 10), bg="#e9ecef")
        self.lbl_stats_treffer.pack(anchor=tk.W, padx=10)
        
        self.lbl_stats_vereine = tk.Label(stats_frame, text="Vereine-Tabelle: Noch nicht geprüft", 
                                         font=("Arial", 10), bg="#e9ecef")
        self.lbl_stats_vereine.pack(anchor=tk.W, padx=10)
        
        # Button: Tabellen prüfen
        self.btn_check = tk.Button(root, text="🔍 Tabellen prüfen", 
                                   command=self.tabellen_pruefen, 
                                   bg="#17a2b8", fg="white", height=2, 
                                   font=("Arial", 11, "bold"))
        self.btn_check.pack(fill=tk.X, padx=20, pady=10)
        
        # Button: Schritt 1 - Erster Abgleich
        self.btn_schritt1 = tk.Button(root, text="⚡ Schritt 1: Ersten Abgleich durchführen", 
                                      command=self.schritt1_abgleich, 
                                      bg="#28a745", fg="white", height=2, state=tk.DISABLED,
                                      font=("Arial", 11, "bold"))
        self.btn_schritt1.pack(fill=tk.X, padx=20, pady=5)
        
        # Button: Schritt 2 - Zweiter Abgleich
        self.btn_schritt2 = tk.Button(root, text="🔄 Schritt 2: Nachfolgenden Abgleich durchführen", 
                                      command=self.schritt2_abgleich, 
                                      bg="#fd7e14", fg="white", height=2, state=tk.DISABLED,
                                      font=("Arial", 11, "bold"))
        self.btn_schritt2.pack(fill=tk.X, padx=20, pady=5)
        
        # Button: Ergebnis anzeigen
        self.btn_show = tk.Button(root, text="📊 Treffer_Verein_Hit anzeigen", 
                                  command=self.ergebnis_anzeigen, 
                                  bg="#6f42c1", fg="white", height=2,
                                  font=("Arial", 11, "bold"))
        self.btn_show.pack(fill=tk.X, padx=20, pady=5)
        
        # Log-Bereich
        tk.Label(root, text="Verarbeitungs-Log:", font=("Arial", 10, "bold")).pack(anchor=tk.W, padx=20, pady=(10,5))
        self.txt_log = scrolledtext.ScrolledText(root, height=20, font=("Courier", 9))
        self.txt_log.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        
        # Button Frame
        btn_frame = tk.Frame(root)
        btn_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Button: Tabelle löschen
        self.btn_clear = tk.Button(btn_frame, text="🗑️ Treffer_Verein_Hit löschen", 
                                   command=self.tabelle_loeschen, 
                                   bg="#dc3545", fg="white", height=2,
                                   font=("Arial", 10, "bold"))
        self.btn_clear.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Button: Vereine-Tabelle anzeigen
        self.btn_show_vereine = tk.Button(btn_frame, text="🏢 Vereine-Tabelle anzeigen", 
                                          command=self.vereine_anzeigen, 
                                          bg="#6c757d", fg="white", height=2,
                                          font=("Arial", 10, "bold"))
        self.btn_show_vereine.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Statusleiste
        self.status_label = tk.Label(root, text="Bereit", bg="#e0e0e0", anchor=tk.W, font=("Arial", 9))
        self.status_label.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Beim Start Tabellen prüfen
        self.root.after(500, self.tabellen_pruefen)
    
    def log(self, message):
        """Fügt eine Nachricht zum Log hinzu"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.txt_log.insert(tk.END, f"[{timestamp}] {message}\n")
        self.txt_log.see(tk.END)
        self.root.update()
    
    def tabellen_pruefen(self):
        """Prüft ob die erforderlichen Tabellen existieren"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Treffer-Tabelle prüfen
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='Treffer'")
            treffer_exists = cursor.fetchone()[0] > 0
            
            if treffer_exists:
                cursor.execute("SELECT COUNT(*) FROM Treffer")
                treffer_count = cursor.fetchone()[0]
                self.lbl_stats_treffer.config(text=f"Treffer-Tabelle: {treffer_count} Einträge vorhanden", 
                                             fg="green")
            else:
                self.lbl_stats_treffer.config(text="Treffer-Tabelle: NICHT VORHANDEN", fg="red")
            
            # Vereine-Tabelle prüfen
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='Vereine'")
            vereine_exists = cursor.fetchone()[0] > 0
            
            if vereine_exists:
                cursor.execute("SELECT COUNT(*) FROM Vereine")
                vereine_count = cursor.fetchone()[0]
                self.lbl_stats_vereine.config(text=f"Vereine-Tabelle: {vereine_count} Einträge vorhanden", 
                                             fg="green")
            else:
                self.lbl_stats_vereine.config(text="Vereine-Tabelle: NICHT VORHANDEN", fg="red")
                # Vereine-Tabelle erstellen
                self.vereine_tabelle_erstellen(cursor)
                self.lbl_stats_vereine.config(text="Vereine-Tabelle: Leer erstellt - bitte Daten importieren", 
                                             fg="orange")
            
            conn.close()
            
            # Buttons aktivieren wenn beide Tabellen vorhanden
            if treffer_exists and vereine_exists:
                self.btn_schritt1.config(state=tk.NORMAL)
                self.log("✅ Beide Tabellen vorhanden - Abgleich kann gestartet werden")
            else:
                self.log("❌ Fehlende Tabellen - bitte erst Daten importieren")
            
        except Exception as e:
            self.log(f"❌ Fehler beim Prüfen der Tabellen: {str(e)}")
            messagebox.showerror("Fehler", f"Fehler beim Prüfen der Tabellen:\n{str(e)}")
    
    def vereine_tabelle_erstellen(self, cursor):
        """Erstellt die Vereine-Tabelle falls sie nicht existiert"""
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Vereine (
                    Verein_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Verein TEXT NOT NULL,
                    Lettern TEXT,
                    Kurzident TEXT,
                    Kurzident2 TEXT
                )
            ''')
            self.log("✅ Vereine-Tabelle wurde erstellt")
        except Exception as e:
            self.log(f"❌ Fehler beim Erstellen der Vereine-Tabelle: {str(e)}")
    
    def schritt1_abgleich(self):
        """Führt den ersten Abgleich durch"""
        try:
            self.btn_schritt1.config(state=tk.DISABLED)
            self.log("🚀 Starte Schritt 1: Ersten Abgleich...")
            
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Treffer_Verein_Hit Tabelle erstellen
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Treffer_Verein_Hit (
                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    zeile_inhalt TEXT NOT NULL,
                    extracted_data_id INTEGER NOT NULL,
                    zeile_inhalt_ohne_treffer TEXT,
                    Verein_ID INTEGER,
                    Verein TEXT,
                    gefunden_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Alle Treffer holen
            cursor.execute("SELECT id, zeile_inhalt, extracted_data_id FROM Treffer")
            treffer_rows = cursor.fetchall()
            
            # Alle Vereine holen
            cursor.execute("SELECT Verein_ID, Verein FROM Vereine WHERE Verein IS NOT NULL AND Verein != ''")
            vereine_rows = cursor.fetchall()
            
            self.log(f"📊 {len(treffer_rows)} Treffer und {len(vereine_rows)} Vereine gefunden")
            
            treffer_count = 0
            
            for treffer_id, zeile_inhalt, extracted_data_id in treffer_rows:
                for verein_id, verein_name in vereine_rows:
                    if verein_name.lower() in zeile_inhalt.lower():
                        # Vereinsname aus zeile_inhalt entfernen
                        zeile_ohne_verein = zeile_inhalt.replace(verein_name, "").strip()
                        # Mehrfache Leerzeichen entfernen
                        zeile_ohne_verein = re.sub(r'\s+', ' ', zeile_ohne_verein)
                        
                        cursor.execute('''
                            INSERT INTO Treffer_Verein_Hit 
                            (zeile_inhalt, extracted_data_id, zeile_inhalt_ohne_treffer, Verein_ID, Verein)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (zeile_inhalt, extracted_data_id, zeile_ohne_verein, verein_id, verein_name))
                        
                        treffer_count += 1
                        
                        if treffer_count % 10 == 0:
                            self.log(f"   💫 {treffer_count} Treffer gefunden...")
                            self.root.update()
            
            conn.commit()
            conn.close()
            
            self.log(f"✅ Schritt 1 abgeschlossen: {treffer_count} Vereins-Treffer gefunden")
            self.status_label.config(text=f"Schritt 1: {treffer_count} Treffer gefunden")
            
            if treffer_count > 0:
                self.btn_schritt2.config(state=tk.NORMAL)
            
            messagebox.showinfo("Schritt 1 abgeschlossen", 
                               f"Erster Abgleich erfolgreich!\n\n{treffer_count} Vereins-Treffer gefunden")
            
        except Exception as e:
            self.log(f"❌ Fehler in Schritt 1: {str(e)}")
            messagebox.showerror("Fehler", f"Fehler in Schritt 1:\n{str(e)}")
        finally:
            self.btn_schritt1.config(state=tk.NORMAL)
    
    def schritt2_abgleich(self):
        """Führt den zweiten Abgleich durch (auf zeile_inhalt_ohne_treffer)"""
        try:
            self.btn_schritt2.config(state=tk.DISABLED)
            self.log("🔄 Starte Schritt 2: Nachfolgenden Abgleich...")
            
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Aktuelle Treffer_Verein_Hit holen
            cursor.execute('''
                SELECT ID, zeile_inhalt, extracted_data_id, zeile_inhalt_ohne_treffer 
                FROM Treffer_Verein_Hit 
                WHERE zeile_inhalt_ohne_treffer IS NOT NULL AND zeile_inhalt_ohne_treffer != ''
            ''')
            hit_rows = cursor.fetchall()
            
            # Alle Vereine holen
            cursor.execute("SELECT Verein_ID, Verein FROM Vereine WHERE Verein IS NOT NULL AND Verein != ''")
            vereine_rows = cursor.fetchall()
            
            self.log(f"📊 {len(hit_rows)} vorhandene Hits prüfen auf weitere Vereine...")
            
            neue_treffer = 0
            
            for hit_id, original_zeile, extracted_data_id, zeile_ohne_treffer in hit_rows:
                for verein_id, verein_name in vereine_rows:
                    if verein_name.lower() in zeile_ohne_treffer.lower():
                        # Vereinsname aus zeile_inhalt_ohne_treffer entfernen
                        neue_zeile_ohne_verein = zeile_ohne_treffer.replace(verein_name, "").strip()
                        # Mehrfache Leerzeichen entfernen
                        neue_zeile_ohne_verein = re.sub(r'\s+', ' ', neue_zeile_ohne_verein)
                        
                        cursor.execute('''
                            INSERT INTO Treffer_Verein_Hit 
                            (zeile_inhalt, extracted_data_id, zeile_inhalt_ohne_treffer, Verein_ID, Verein)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (original_zeile, extracted_data_id, neue_zeile_ohne_verein, verein_id, verein_name))
                        
                        neue_treffer += 1
                        
                        if neue_treffer % 5 == 0:
                            self.log(f"   💫 {neue_treffer} zusätzliche Treffer gefunden...")
                            self.root.update()
            
            conn.commit()
            conn.close()
            
            self.log(f"✅ Schritt 2 abgeschlossen: {neue_treffer} zusätzliche Vereins-Treffer gefunden")
            self.status_label.config(text=f"Schritt 2: {neue_treffer} zusätzliche Treffer gefunden")
            
            messagebox.showinfo("Schritt 2 abgeschlossen", 
                               f"Zweiter Abgleich erfolgreich!\n\n{neue_treffer} zusätzliche Vereins-Treffer gefunden")
            
        except Exception as e:
            self.log(f"❌ Fehler in Schritt 2: {str(e)}")
            messagebox.showerror("Fehler", f"Fehler in Schritt 2:\n{str(e)}")
        finally:
            self.btn_schritt2.config(state=tk.NORMAL)
    
    def ergebnis_anzeigen(self):
        """Zeigt die Treffer_Verein_Hit Tabelle an"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='Treffer_Verein_Hit'")
            if cursor.fetchone()[0] == 0:
                messagebox.showinfo("Keine Tabelle", "Tabelle 'Treffer_Verein_Hit' existiert noch nicht!\nFühren Sie zuerst einen Abgleich durch.")
                conn.close()
                return
            
            cursor.execute("SELECT COUNT(*) FROM Treffer_Verein_Hit")
            anzahl = cursor.fetchone()[0]
            
            if anzahl == 0:
                messagebox.showinfo("Keine Daten", "Tabelle 'Treffer_Verein_Hit' ist leer!")
                conn.close()
                return
            
            cursor.execute('''
                SELECT ID, zeile_inhalt, extracted_data_id, zeile_inhalt_ohne_treffer, Verein_ID, Verein, gefunden_am
                FROM Treffer_Verein_Hit 
                ORDER BY ID DESC
            ''')
            rows = cursor.fetchall()
            conn.close()
            
            # Neues Fenster
            result_window = tk.Toplevel(self.root)
            result_window.title("Treffer_Verein_Hit")
            result_window.geometry("1400x700")
            
            tk.Label(result_window, text=f"Treffer_Verein_Hit ({anzahl} Einträge)", 
                    font=("Arial", 12, "bold"), bg="#e8f5e8", pady=10).pack(fill=tk.X)
            
            # Treeview
            tree_frame = tk.Frame(result_window)
            tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            vsb = tk.Scrollbar(tree_frame, orient="vertical")
            vsb.pack(side=tk.RIGHT, fill=tk.Y)
            
            hsb = tk.Scrollbar(tree_frame, orient="horizontal")
            hsb.pack(side=tk.BOTTOM, fill=tk.X)
            
            tree = ttk.Treeview(tree_frame, yscrollcommand=vsb.set, xscrollcommand=hsb.set)
            tree.pack(fill=tk.BOTH, expand=True)
            
            vsb.config(command=tree.yview)
            hsb.config(command=tree.xview)
            
            # Spalten
            spalten = ("ID", "Zeile_Inhalt", "Extracted_Data_ID", "Zeile_ohne_Verein", "Verein_ID", "Verein", "Gefunden_am")
            tree["columns"] = spalten
            tree["show"] = "headings"
            
            for col in spalten:
                tree.heading(col, text=col)
                tree.column(col, width=150, anchor=tk.W)
            
            for row in rows:
                tree.insert("", tk.END, values=row)
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Anzeigen der Ergebnisse:\n{str(e)}")
    
    def vereine_anzeigen(self):
        """Zeigt die Vereine-Tabelle an"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM Vereine")
            anzahl = cursor.fetchone()[0]
            
            cursor.execute("SELECT * FROM Vereine ORDER BY Verein_ID")
            rows = cursor.fetchall()
            conn.close()
            
            # Neues Fenster
            vereine_window = tk.Toplevel(self.root)
            vereine_window.title("Vereine-Tabelle")
            vereine_window.geometry("1000x600")
            
            tk.Label(vereine_window, text=f"Vereine-Tabelle ({anzahl} Einträge)", 
                    font=("Arial", 12, "bold"), bg="#fff3cd", pady=10).pack(fill=tk.X)
            
            # Treeview
            tree_frame = tk.Frame(vereine_window)
            tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            vsb = tk.Scrollbar(tree_frame, orient="vertical")
            vsb.pack(side=tk.RIGHT, fill=tk.Y)
            
            tree = ttk.Treeview(tree_frame, yscrollcommand=vsb.set)
            tree.pack(fill=tk.BOTH, expand=True)
            
            vsb.config(command=tree.yview)
            
            # Spalten
            spalten = ("Verein_ID", "Verein", "Lettern", "Kurzident", "Kurzident2")
            tree["columns"] = spalten
            tree["show"] = "headings"
            
            for col in spalten:
                tree.heading(col, text=col)
                tree.column(col, width=150, anchor=tk.W)
            
            for row in rows:
                tree.insert("", tk.END, values=row)
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Anzeigen der Vereine:\n{str(e)}")
    
    def tabelle_loeschen(self):
        """Löscht die Treffer_Verein_Hit Tabelle"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='Treffer_Verein_Hit'")
            if cursor.fetchone()[0] == 0:
                messagebox.showinfo("Keine Tabelle", "Tabelle 'Treffer_Verein_Hit' existiert nicht!")
                conn.close()
                return
            
            cursor.execute("SELECT COUNT(*) FROM Treffer_Verein_Hit")
            anzahl = cursor.fetchone()[0]
            
            antwort = messagebox.askyesno("Tabelle löschen?", 
                                         f"Möchten Sie die Tabelle 'Treffer_Verein_Hit' mit {anzahl} Einträgen wirklich löschen?\n\n"
                                         "Diese Aktion kann NICHT rückgängig gemacht werden!",
                                         icon='warning')
            
            if antwort:
                cursor.execute("DROP TABLE Treffer_Verein_Hit")
                conn.commit()
                conn.close()
                
                self.log("🗑️ Treffer_Verein_Hit Tabelle wurde gelöscht")
                messagebox.showinfo("Gelöscht", "Tabelle 'Treffer_Verein_Hit' wurde gelöscht!")
                self.btn_schritt2.config(state=tk.DISABLED)
            else:
                conn.close()
                
        except Exception as e:
            self.log(f"❌ Fehler beim Löschen: {str(e)}")
            messagebox.showerror("Fehler", f"Fehler beim Löschen der Tabelle:\n{str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = VereinTrefferApp(root)
    root.mainloop()