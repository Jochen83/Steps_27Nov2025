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
        self.btn_schritt1 = tk.Button(root, text="⚡ Schritt 1: Abgleich durchführen", 
                                      command=self.schritt1_abgleich, 
                                      bg="#28a745", fg="white", height=2, state=tk.DISABLED,
                                      font=("Arial", 11, "bold"))
        self.btn_schritt1.pack(fill=tk.X, padx=20, pady=5)
        
        # Button: Schritt 2 - Weiterer Abgleich mit Treffer_Verein_Hit
        self.btn_schritt2 = tk.Button(root, text="🔄 Schritt 2: Weiterer Abgleich (Treffer_Verein_Hit)", 
                                      command=self.schritt2_abgleich, 
                                      bg="#fd7e14", fg="white", height=2, state=tk.DISABLED,
                                      font=("Arial", 11, "bold"))
        self.btn_schritt2.pack(fill=tk.X, padx=20, pady=5)
        
        # Button: Abgleich erneut durchführen
        self.btn_erneut = tk.Button(root, text="♾️ Abgleich erneut durchführen", 
                                    command=self.abgleich_erneut, 
                                    bg="#28a745", fg="white", height=2, state=tk.DISABLED,
                                    font=("Arial", 11, "bold"))
        self.btn_erneut.pack(fill=tk.X, padx=20, pady=5)
        
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
            
                        
            conn.close()
            
            # Buttons aktivieren wenn beide Tabellen vorhanden
            if treffer_exists and vereine_exists:
                self.btn_schritt1.config(state=tk.NORMAL)
                self.btn_erneut.config(state=tk.NORMAL)
                self.log("✅ Beide Tabellen vorhanden - Abgleich kann gestartet werden")
            else:
                self.log("❌ Fehlende Tabellen - bitte erst Daten importieren")
            
        except Exception as e:
            self.log(f"❌ Fehler beim Prüfen der Tabellen: {str(e)}")
            messagebox.showerror("Fehler", f"Fehler beim Prüfen der Tabellen:\n{str(e)}")
    
    
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
                    zeile_inhalt_orig TEXT,
                    extracted_data_id INTEGER NOT NULL,
                    zeile_inhalt_ohne_treffer TEXT,
                    Verein_DRVID TEXT,
                    Verein TEXT,
                    gefunden_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Alle Treffer holen
            cursor.execute("SELECT id, zeile_inhalt, extracted_data_id FROM Treffer")
            treffer_rows = cursor.fetchall()
            
            # Alle Vereine holen
            cursor.execute("SELECT Verein_DRVID, Verein FROM Vereine WHERE Verein IS NOT NULL AND Verein != ''")
            vereine_rows = cursor.fetchall()
            
            self.log(f"📊 {len(treffer_rows)} Treffer und {len(vereine_rows)} Vereine gefunden")
            
            treffer_count = 0
            
            # Einfacher Durchlauf: Jede Treffer-Zeile mit allen Vereinen abgleichen
            for i, (treffer_id, zeile_inhalt, extracted_data_id) in enumerate(treffer_rows, 1):
                self.log(f"🔍 Prüfe Zeile {i}/{len(treffer_rows)} (ID: {treffer_id})...")
                
                treffer_gefunden = False
                
                # Durch alle Vereine für diese Treffer-Zeile
                for Verein_DRVID, verein_name in vereine_rows:
                    if verein_name.lower() in zeile_inhalt.lower():
                        # Ursprünglichen Inhalt in zeile_inhalt_orig speichern
                        zeile_inhalt_orig = zeile_inhalt
                        
                        # Vereinsname aus zeile_inhalt entfernen
                        zeile_inhalt_neu = zeile_inhalt.replace(verein_name, "").strip()
                        # Mehrfache Leerzeichen entfernen
                        zeile_inhalt_neu = re.sub(r'\s+', ' ', zeile_inhalt_neu)
                        
                        # Vereinsname aus zeile_inhalt entfernen für zeile_inhalt_ohne_treffer
                        zeile_ohne_verein = zeile_inhalt.replace(verein_name, "").strip()
                        # Mehrfache Leerzeichen entfernen
                        zeile_ohne_verein = re.sub(r'\s+', ' ', zeile_ohne_verein)
                        
                        cursor.execute('''
                            INSERT INTO Treffer_Verein_Hit 
                            (zeile_inhalt, zeile_inhalt_orig, extracted_data_id, zeile_inhalt_ohne_treffer, Verein_DRVID, Verein)
                            VALUES (?, ?, ?, ?, ?, ?)
                        ''', (zeile_inhalt_neu, zeile_inhalt_orig, extracted_data_id, zeile_ohne_verein, Verein_DRVID, verein_name))
                        
                        treffer_count += 1
                        self.log(f"   ✅ Treffer {treffer_count}: '{verein_name}' in Zeile {treffer_id}")
                        treffer_gefunden = True
                        break  # Sofort nach erstem Treffer zur nächsten Zeile
                
                if not treffer_gefunden:
                    self.log(f"   ❌ Kein Verein gefunden in Zeile {treffer_id}")
                
                # Fortschritt anzeigen
                if i % 10 == 0:
                    self.root.update()
            
            conn.commit()
            conn.close()
            
            self.log(f"✅ Schritt 1 abgeschlossen: {treffer_count} Vereins-Treffer gefunden")
            self.status_label.config(text=f"Schritt 1 abgeschlossen: {treffer_count} Treffer gefunden")
            
            # Schritt 2 Button aktivieren wenn Treffer gefunden wurden
            if treffer_count > 0:
                self.btn_schritt2.config(state=tk.NORMAL)
                self.log("🔄 Schritt 2 kann jetzt durchgeführt werden")
            
            messagebox.showinfo("Schritt 1 abgeschlossen", 
                               f"Erster Abgleich erfolgreich!\n\n{treffer_count} Vereins-Treffer gefunden")
            
        except Exception as e:
            self.log(f"❌ Fehler in Schritt 1: {str(e)}")
            messagebox.showerror("Fehler", f"Fehler in Schritt 1:\n{str(e)}")
        finally:
            self.btn_schritt1.config(state=tk.NORMAL)
    
    def schritt2_abgleich(self):
        """Führt den zweiten Abgleich mit Treffer_Verein_Hit als Quelle durch"""
        try:
            self.btn_schritt2.config(state=tk.DISABLED)
            self.log("🔄 Starte Schritt 2: Weiterer Abgleich mit Treffer_Verein_Hit...")
            
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Alle Einträge aus Treffer_Verein_Hit als Quelle holen
            cursor.execute("SELECT ID, zeile_inhalt, zeile_inhalt_orig, extracted_data_id FROM Treffer_Verein_Hit WHERE zeile_inhalt IS NOT NULL AND zeile_inhalt != ''")
            hit_rows = cursor.fetchall()
            
            # Alle Vereine holen
            cursor.execute("SELECT Verein_DRVID, Verein FROM Vereine WHERE Verein IS NOT NULL AND Verein != ''")
            vereine_rows = cursor.fetchall()
            
            self.log(f"📊 {len(hit_rows)} Treffer_Verein_Hit Einträge und {len(vereine_rows)} Vereine gefunden")
            
            neue_treffer = 0
            
            # Durchlauf durch alle Treffer_Verein_Hit Einträge
            for i, (hit_id, zeile_inhalt, zeile_inhalt_orig, extracted_data_id) in enumerate(hit_rows, 1):
                self.log(f"🔍 Prüfe Hit-Zeile {i}/{len(hit_rows)} (ID: {hit_id})...")
                
                treffer_gefunden = False
                
                # Durch alle Vereine für diese Hit-Zeile
                for Verein_DRVID, verein_name in vereine_rows:
                    if verein_name.lower() in zeile_inhalt.lower():
                        # Vereinsname aus zeile_inhalt entfernen
                        zeile_inhalt_neu = zeile_inhalt.replace(verein_name, "").strip()
                        # Mehrfache Leerzeichen entfernen
                        zeile_inhalt_neu = re.sub(r'\s+', ' ', zeile_inhalt_neu)
                        
                        # Vereinsname aus zeile_inhalt entfernen für zeile_inhalt_ohne_treffer
                        zeile_ohne_verein = zeile_inhalt.replace(verein_name, "").strip()
                        # Mehrfache Leerzeichen entfernen
                        zeile_ohne_verein = re.sub(r'\s+', ' ', zeile_ohne_verein)
                        
                        # An Ende der Tabelle anfügen
                        cursor.execute('''
                            INSERT INTO Treffer_Verein_Hit 
                            (zeile_inhalt, zeile_inhalt_orig, extracted_data_id, zeile_inhalt_ohne_treffer, Verein_DRVID, Verein)
                            VALUES (?, ?, ?, ?, ?, ?)
                        ''', (zeile_inhalt_neu, zeile_inhalt_orig, extracted_data_id, zeile_ohne_verein, Verein_DRVID, verein_name))
                        
                        neue_treffer += 1
                        self.log(f"   ✅ Neuer Treffer {neue_treffer}: '{verein_name}' in Hit-ID {hit_id}")
                        treffer_gefunden = True
                        break  # Sofort nach erstem Treffer zur nächsten Zeile
                
                if not treffer_gefunden:
                    self.log(f"   ❌ Kein weiterer Verein gefunden in Hit-ID {hit_id}")
                
                # Fortschritt anzeigen
                if i % 10 == 0:
                    self.root.update()
            
            conn.commit()
            conn.close()
            
            self.log(f"✅ Schritt 2 abgeschlossen: {neue_treffer} zusätzliche Vereins-Treffer gefunden")
            self.status_label.config(text=f"Schritt 2 abgeschlossen: {neue_treffer} zusätzliche Treffer gefunden")
            
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
                SELECT ID, zeile_inhalt, zeile_inhalt_orig, extracted_data_id, zeile_inhalt_ohne_treffer, Verein_DRVID, Verein, gefunden_am
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
            spalten = ("ID", "Zeile_Inhalt", "Zeile_Inhalt_Orig", "Extracted_Data_ID", "Zeile_ohne_Verein", "Verein_DRVID", "Verein", "Gefunden_am")
            tree["columns"] = spalten
            tree["show"] = "headings"
            
            # Variable für Sortierung (erweitert für 2 Spalten)
            sort_reverse = {}
            sort_order = []  # Liste der Sortierspalten in Reihenfolge
            
            def sortiere_spalte(col):
                """Sortiert die Treeview-Spalte auf- oder absteigend mit Unterstützung für 2-Spalten-Sortierung"""
                try:
                    # Ctrl-Taste gedrückt? Dann sekundäre Sortierung
                    is_secondary = len(sort_order) > 0 and col != sort_order[0]
                    
                    if col in sort_order:
                        # Spalte bereits in Sortierung - Richtung umkehren
                        sort_reverse[col] = not sort_reverse.get(col, False)
                    else:
                        # Neue Spalte - aufsteigend starten
                        sort_reverse[col] = False
                        
                        # Zur Sortierliste hinzufügen (max 2 Spalten)
                        if col in sort_order:
                            sort_order.remove(col)
                        sort_order.insert(0, col)
                        if len(sort_order) > 2:
                            # Älteste Sortierung entfernen
                            old_col = sort_order.pop()
                            if old_col in sort_reverse:
                                del sort_reverse[old_col]
                    
                    # Daten aus Treeview holen
                    daten = []
                    for child in tree.get_children(""):
                        row_values = []
                        for spalte in spalten:
                            row_values.append(tree.set(child, spalte))
                        daten.append((row_values, child))
                    
                    # Sortierlogik für bis zu 2 Spalten
                    def sort_key(item):
                        row_values = item[0]
                        keys = []
                        
                        for sort_col in sort_order:
                            if sort_col in spalten:
                                col_index = list(spalten).index(sort_col)
                                value = row_values[col_index]
                                
                                # Nach Datentyp sortieren
                                if sort_col in ["ID", "Extracted_Data_ID"]:
                                    # Numerische Sortierung
                                    sort_value = int(value) if value and value.isdigit() else 0
                                else:
                                    # Alphabetische Sortierung (case-insensitive)
                                    sort_value = str(value).lower() if value else ""
                                
                                # Bei absteigender Sortierung negieren (für Zahlen) oder umkehren
                                if sort_reverse.get(sort_col, False):
                                    if isinstance(sort_value, int):
                                        sort_value = -sort_value
                                    else:
                                        sort_value = ''.join(reversed(sort_value))
                                
                                keys.append(sort_value)
                        
                        return tuple(keys) if keys else (0,)
                    
                    # Sortieren
                    daten.sort(key=sort_key)
                    
                    # Treeview neu anordnen
                    for index, (row_values, child) in enumerate(daten):
                        tree.move(child, "", index)
                    
                    # Alle Überschriften zurücksetzen
                    for spalte in spalten:
                        clean_text = spalte.replace(" ▲", "").replace(" ▼", "").replace(" ①", "").replace(" ②", "")
                        tree.heading(spalte, text=clean_text, command=lambda c=spalte: sortiere_spalte(c))
                    
                    # Sortier-Indikatoren setzen
                    for i, sort_col in enumerate(sort_order):
                        if sort_col in spalten:
                            # Pfeil für Richtung
                            pfeil = " ▼" if sort_reverse.get(sort_col, False) else " ▲"
                            # Nummer für Priorität
                            nummer = f" ①" if i == 0 else f" ②"
                            
                            clean_col = sort_col.replace(" ▲", "").replace(" ▼", "").replace(" ①", "").replace(" ②", "")
                            tree.heading(sort_col, text=clean_col + pfeil + nummer, command=lambda c=sort_col: sortiere_spalte(c))
                    
                except Exception as e:
                    print(f"Fehler beim Sortieren: {str(e)}")
            
            # Spaltenüberschriften mit Sortier-Funktion konfigurieren
            for col in spalten:
                tree.heading(col, text=col, command=lambda c=col: sortiere_spalte(c))
                tree.column(col, width=150, anchor=tk.W)
                sort_reverse[col] = False  # Standard: aufsteigend
            
            # Info-Text für Benutzer
            info_text = tk.Label(result_window, 
                               text="💡 Tipp: Klicken Sie auf Spaltenüberschriften zum Sortieren. Bis zu 2 Spalten gleichzeitig möglich (① = Primär, ② = Sekundär)", 
                               font=("Arial", 9), fg="gray", pady=5)
            info_text.pack()
            
            # Daten in Treeview einfügen
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
            
            cursor.execute("SELECT * FROM Vereine ORDER BY Verein_DRVID")
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
            spalten = ("Verein_DRVID", "Verein", "Lettern", "Kurzident", "Kurzident2")
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
                # Schritt 2 Button deaktivieren da Tabelle gelöscht
                self.btn_schritt2.config(state=tk.DISABLED)
            else:
                conn.close()
                
        except Exception as e:
            self.log(f"❌ Fehler beim Löschen: {str(e)}")
            messagebox.showerror("Fehler", f"Fehler beim Löschen der Tabelle:\n{str(e)}")
    
    def abgleich_erneut(self):
        """Führt den kompletten Abgleich erneut durch (Schritt 1 + 2)"""
        try:
            # Bestätigung
            antwort = messagebox.askyesno(
                "Abgleich erneut durchführen?",
                "Möchten Sie den kompletten Abgleich erneut durchführen?\n\n"
                "Dies führt beide Schritte nacheinander aus:\n"
                "- Schritt 1: Erster Abgleich (Treffer → Vereine)\n"
                "- Schritt 2: Weiterer Abgleich (Treffer_Verein_Hit → Vereine)\n\n"
                "Vorhandene Treffer_Verein_Hit Tabelle wird gelöscht!",
                icon='question'
            )
            
            if not antwort:
                return
            
            self.btn_erneut.config(state=tk.DISABLED)
            self.log("🚀 Starte kompletten Abgleich erneut...")
            
            # Zuerst Treffer_Verein_Hit Tabelle löschen (falls vorhanden)
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='Treffer_Verein_Hit'")
            if cursor.fetchone()[0] > 0:
                cursor.execute("DROP TABLE Treffer_Verein_Hit")
                conn.commit()
                self.log("🗑️ Alte Treffer_Verein_Hit Tabelle gelöscht")
            
            conn.close()
            
            # Buttons zurücksetzen
            self.btn_schritt2.config(state=tk.DISABLED)
            
            # Schritt 1 ausführen
            self.log("⚡ Starte Schritt 1...")
            treffer_count_1 = self.schritt1_abgleich_intern()
            
            # Kurze Pause
            self.root.after(100)
            
            # Schritt 2 ausführen wenn Treffer aus Schritt 1 vorhanden
            if treffer_count_1 > 0:
                self.log("🔄 Starte Schritt 2...")
                treffer_count_2 = self.schritt2_abgleich_intern()
                gesamt_treffer = treffer_count_1 + treffer_count_2
            else:
                treffer_count_2 = 0
                gesamt_treffer = treffer_count_1
            
            self.log(f"✅ Kompletter Abgleich erfolgreich abgeschlossen! Gesamt: {gesamt_treffer} Treffer")
            messagebox.showinfo("Abgleich abgeschlossen", 
                               f"Der komplette Abgleich wurde erfolgreich durchgeführt!\n\n"
                               f"Schritt 1: {treffer_count_1} Treffer\n"
                               f"Schritt 2: {treffer_count_2} Treffer\n"
                               f"Gesamt: {gesamt_treffer} Treffer")
            
        except Exception as e:
            self.log(f"❌ Fehler beim erneuten Abgleich: {str(e)}")
            messagebox.showerror("Fehler", f"Fehler beim erneuten Abgleich:\n{str(e)}")
        finally:
            self.btn_erneut.config(state=tk.NORMAL)
    
    def schritt1_abgleich_intern(self):
        """Interne Methode für Schritt 1 (ohne GUI-Updates)"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Treffer_Verein_Hit Tabelle erstellen
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Treffer_Verein_Hit (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                zeile_inhalt TEXT NOT NULL,
                zeile_inhalt_orig TEXT,
                extracted_data_id INTEGER NOT NULL,
                zeile_inhalt_ohne_treffer TEXT,
                Verein_DRVID TEXT,
                Verein TEXT,
                gefunden_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Alle Treffer holen
        cursor.execute("SELECT id, zeile_inhalt, extracted_data_id FROM Treffer")
        treffer_rows = cursor.fetchall()
        
        # Alle Vereine holen
        cursor.execute("SELECT Verein_DRVID, Verein FROM Vereine WHERE Verein IS NOT NULL AND Verein != ''")
        vereine_rows = cursor.fetchall()
        
        treffer_count = 0
        
        # Mittlere Schleife: Durch alle Treffer-Zeilen
        for treffer_id, zeile_inhalt, extracted_data_id in treffer_rows:
            treffer_gefunden = False
            
            # Innere Schleife: Durch alle Vereine für diese Quellzeile
            for Verein_DRVID, verein_name in vereine_rows:
                if verein_name.lower() in zeile_inhalt.lower():
                    # Ursprünglichen Inhalt in zeile_inhalt_orig speichern
                    zeile_inhalt_orig = zeile_inhalt
                    
                    # Vereinsname aus zeile_inhalt entfernen
                    zeile_inhalt_neu = zeile_inhalt.replace(verein_name, "").strip()
                    zeile_inhalt_neu = re.sub(r'\s+', ' ', zeile_inhalt_neu)
                    
                    # Vereinsname aus zeile_inhalt entfernen für zeile_inhalt_ohne_treffer
                    zeile_ohne_verein = zeile_inhalt.replace(verein_name, "").strip()
                    zeile_ohne_verein = re.sub(r'\s+', ' ', zeile_ohne_verein)
                    
                    cursor.execute('''
                        INSERT INTO Treffer_Verein_Hit 
                        (zeile_inhalt, zeile_inhalt_orig, extracted_data_id, zeile_inhalt_ohne_treffer, Verein_DRVID, Verein)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (zeile_inhalt_neu, zeile_inhalt_orig, extracted_data_id, zeile_ohne_verein, Verein_DRVID, verein_name))
                    
                    treffer_count += 1
                    treffer_gefunden = True
                    break  # Sofort nach erstem Treffer zur nächsten Zeile
        
        conn.commit()
        conn.close()
        self.log(f"✅ Schritt 1 intern: {treffer_count} Vereins-Treffer gefunden")
        return treffer_count
    
    def schritt2_abgleich_intern(self):
        """Interne Methode für Schritt 2 (ohne GUI-Updates)"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Alle Einträge aus Treffer_Verein_Hit als Quelle holen
        cursor.execute("SELECT ID, zeile_inhalt, zeile_inhalt_orig, extracted_data_id FROM Treffer_Verein_Hit WHERE zeile_inhalt IS NOT NULL AND zeile_inhalt != ''")
        hit_rows = cursor.fetchall()
        
        # Alle Vereine holen
        cursor.execute("SELECT Verein_DRVID, Verein FROM Vereine WHERE Verein IS NOT NULL AND Verein != ''")
        vereine_rows = cursor.fetchall()
        
        neue_treffer = 0
        
        # Durchlauf durch alle Treffer_Verein_Hit Einträge
        for hit_id, zeile_inhalt, zeile_inhalt_orig, extracted_data_id in hit_rows:
            treffer_gefunden = False
            
            # Durch alle Vereine für diese Hit-Zeile
            for Verein_DRVID, verein_name in vereine_rows:
                if verein_name.lower() in zeile_inhalt.lower():
                    # Vereinsname aus zeile_inhalt entfernen
                    zeile_inhalt_neu = zeile_inhalt.replace(verein_name, "").strip()
                    zeile_inhalt_neu = re.sub(r'\s+', ' ', zeile_inhalt_neu)
                    
                    # Vereinsname aus zeile_inhalt entfernen für zeile_inhalt_ohne_treffer
                    zeile_ohne_verein = zeile_inhalt.replace(verein_name, "").strip()
                    zeile_ohne_verein = re.sub(r'\s+', ' ', zeile_ohne_verein)
                    
                    # An Ende der Tabelle anfügen
                    cursor.execute('''
                        INSERT INTO Treffer_Verein_Hit 
                        (zeile_inhalt, zeile_inhalt_orig, extracted_data_id, zeile_inhalt_ohne_treffer, Verein_DRVID, Verein)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (zeile_inhalt_neu, zeile_inhalt_orig, extracted_data_id, zeile_ohne_verein, Verein_DRVID, verein_name))
                    
                    neue_treffer += 1
                    treffer_gefunden = True
                    break  # Sofort nach erstem Treffer zur nächsten Zeile
        
        conn.commit()
        conn.close()
        self.log(f"✅ Schritt 2 intern: {neue_treffer} zusätzliche Vereins-Treffer gefunden")
        return neue_treffer


if __name__ == "__main__":
    root = tk.Tk()
    app = VereinTrefferApp(root)
    root.mainloop()