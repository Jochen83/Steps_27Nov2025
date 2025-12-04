import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import os
import shutil
from datetime import datetime

# Tabellen-Abgleich Tool für regatta_unified.db
# Erstellt am 30.11.2025

class TabellenAbgleichApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tabellen-Abgleich Tool")
        self.root.geometry("900x700")
        
        # Variablen
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_name = os.path.join(script_dir, "regatta_unified.db")
        self.backup_dir = os.path.join(script_dir, "BackImport")
        
        # Backup-Verzeichnis erstellen
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # GUI erstellen
        self.gui_erstellen()
        
        # Tabellen beim Start laden
        self.tabellen_laden()
    
    def gui_erstellen(self):
        """Erstellt die GUI-Elemente"""
        
        # Titel
        titel_label = tk.Label(self.root, text="Tabellen-Abgleich Tool", 
                               font=("Arial", 16, "bold"), bg="#e8f5e8", pady=15)
        titel_label.pack(fill=tk.X)
        
        # Info Frame
        info_frame = tk.Frame(self.root, bg="#fff3cd", pady=10)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(info_frame, text="🔍 Gleicht Tabellen-Inhalte basierend auf konfigurierbaren Regeln ab", 
                 font=("Arial", 10), bg="#fff3cd").pack()
        
        # Hauptcontainer
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Quell-Tabelle (ZeilenTypen_Such)
        quell_frame = tk.LabelFrame(main_frame, text="Quell-Tabelle (Suchregeln)", 
                                    font=("Arial", 12, "bold"), pady=10)
        quell_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Quell-Tabelle Auswahl
        tk.Label(quell_frame, text="Quell-Tabelle:", font=("Arial", 10, "bold")).grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.combo_quell_tabelle = ttk.Combobox(quell_frame, font=("Arial", 10), 
                                                width=30, state="readonly")
        self.combo_quell_tabelle.grid(row=0, column=1, padx=5, pady=5)
        self.combo_quell_tabelle.bind("<<ComboboxSelected>>", self.quell_tabelle_geaendert)
        
        # Quell-Felder
        tk.Label(quell_frame, text="QuellWort Feld:", font=("Arial", 10)).grid(
            row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.combo_quell_wort = ttk.Combobox(quell_frame, font=("Arial", 10), 
                                             width=30, state="readonly")
        self.combo_quell_wort.grid(row=1, column=1, padx=5, pady=2)
        
        tk.Label(quell_frame, text="TypNutzkurz Feld:", font=("Arial", 10)).grid(
            row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.combo_typ_nutzkurz = ttk.Combobox(quell_frame, font=("Arial", 10), 
                                               width=30, state="readonly")
        self.combo_typ_nutzkurz.grid(row=2, column=1, padx=5, pady=2)
        
        tk.Label(quell_frame, text="Vergleich_Ganz_Teil Feld:", font=("Arial", 10)).grid(
            row=3, column=0, sticky=tk.W, padx=5, pady=2)
        self.combo_vergleich_typ = ttk.Combobox(quell_frame, font=("Arial", 10), 
                                                width=30, state="readonly")
        self.combo_vergleich_typ.grid(row=3, column=1, padx=5, pady=2)
        
        tk.Label(quell_frame, text="SuchBeginnTeilstring Feld:", font=("Arial", 10)).grid(
            row=4, column=0, sticky=tk.W, padx=5, pady=2)
        self.combo_such_beginn = ttk.Combobox(quell_frame, font=("Arial", 10), 
                                              width=30, state="readonly")
        self.combo_such_beginn.grid(row=4, column=1, padx=5, pady=2)
        
        tk.Label(quell_frame, text="IDZeilenTyp Feld:", font=("Arial", 10)).grid(
            row=5, column=0, sticky=tk.W, padx=5, pady=2)
        self.combo_id_zeilen_typ = ttk.Combobox(quell_frame, font=("Arial", 10), 
                                                width=30, state="readonly")
        self.combo_id_zeilen_typ.grid(row=5, column=1, padx=5, pady=2)
        
        # Ziel-Tabelle
        ziel_frame = tk.LabelFrame(main_frame, text="Ziel-Tabelle (zu bearbeitende Daten)", 
                                   font=("Arial", 12, "bold"), pady=10)
        ziel_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(ziel_frame, text="Ziel-Tabelle:", font=("Arial", 10, "bold")).grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.combo_ziel_tabelle = ttk.Combobox(ziel_frame, font=("Arial", 10), 
                                               width=30, state="readonly")
        self.combo_ziel_tabelle.grid(row=0, column=1, padx=5, pady=5)
        self.combo_ziel_tabelle.bind("<<ComboboxSelected>>", self.ziel_tabelle_geaendert)
        
        tk.Label(ziel_frame, text="Inhalt Feld:", font=("Arial", 10)).grid(
            row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.combo_ziel_inhalt = ttk.Combobox(ziel_frame, font=("Arial", 10), 
                                              width=30, state="readonly")
        self.combo_ziel_inhalt.grid(row=1, column=1, padx=5, pady=2)
        
        tk.Label(ziel_frame, text="Typ Feld:", font=("Arial", 10)).grid(
            row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.combo_ziel_typ = ttk.Combobox(ziel_frame, font=("Arial", 10), 
                                           width=30, state="readonly")
        self.combo_ziel_typ.grid(row=2, column=1, padx=5, pady=2)
        
        # Button Frame
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        # Backup und Start Button
        self.btn_backup = tk.Button(button_frame, text="📁 Backup erstellen", 
                                     command=self.backup_erstellen,
                                     bg="#17a2b8", fg="white", height=2, width=15,
                                     font=("Arial", 11, "bold"))
        self.btn_backup.pack(side=tk.LEFT, padx=(0, 5))
        
        self.btn_ziel_anzeigen = tk.Button(button_frame, text="👁️ Ziel-Tabelle anzeigen", 
                                           command=self.ziel_tabelle_anzeigen,
                                           bg="#6f42c1", fg="white", height=2, width=20,
                                           font=("Arial", 10, "bold"))
        self.btn_ziel_anzeigen.pack(side=tk.LEFT, padx=(0, 5))
        
        self.btn_start = tk.Button(button_frame, text="🔄 Abgleich starten", 
                                   command=self.abgleich_starten,
                                   bg="#28a745", fg="white", height=2, width=15,
                                   font=("Arial", 11, "bold"))
        self.btn_start.pack(side=tk.LEFT)
        
        # Fortschritts-Frame
        progress_frame = tk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=(10, 0))
        
        tk.Label(progress_frame, text="Fortschritt:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        
        self.progress = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress.pack(fill=tk.X, pady=5)
        
        self.lbl_status = tk.Label(progress_frame, text="Bereit für Abgleich", 
                                   font=("Arial", 10), fg="grey")
        self.lbl_status.pack(anchor=tk.W)
        
        # Ergebnis-Textbereich
        tk.Label(main_frame, text="Abgleich-Protokoll:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(10,5))
        
        text_frame = tk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.txt_protokoll = tk.Text(text_frame, height=15, font=("Courier", 9))
        scrollbar = tk.Scrollbar(text_frame, command=self.txt_protokoll.yview)
        self.txt_protokoll.config(yscrollcommand=scrollbar.set)
        
        self.txt_protokoll.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Statusleiste
        self.status_label = tk.Label(self.root, text="Bereit", bg="#e0e0e0", 
                                     anchor=tk.W, font=("Arial", 9))
        self.status_label.pack(fill=tk.X, side=tk.BOTTOM)
    
    def tabellen_laden(self):
        """Lädt alle verfügbaren Tabellen"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
            tabellen = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            self.combo_quell_tabelle['values'] = tabellen
            self.combo_ziel_tabelle['values'] = tabellen
            
            # Standard-Werte setzen
            if 'ZeilenTypen_Such' in tabellen:
                self.combo_quell_tabelle.set('ZeilenTypen_Such')
                self.quell_felder_laden()
            
            if any('GA_ER_2023' in t for t in tabellen):
                ga_table = next(t for t in tabellen if 'GA_ER_2023' in t)
                self.combo_ziel_tabelle.set(ga_table)
                self.ziel_felder_laden()
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Laden der Tabellen:\n{str(e)}")
    
    def quell_tabelle_geaendert(self, event=None):
        """Wird aufgerufen wenn Quell-Tabelle geändert wird"""
        self.quell_felder_laden()
    
    def ziel_tabelle_geaendert(self, event=None):
        """Wird aufgerufen wenn Ziel-Tabelle geändert wird"""
        self.ziel_felder_laden()
    
    def quell_felder_laden(self):
        """Lädt die Felder der Quell-Tabelle"""
        tabelle = self.combo_quell_tabelle.get()
        if not tabelle:
            return
        
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute(f'PRAGMA table_info({tabelle})')
            felder_info = cursor.fetchall()
            felder = [info[1] for info in felder_info]
            conn.close()
            
            # Alle Comboboxen mit den gleichen Feldern füllen
            for combo in [self.combo_quell_wort, self.combo_typ_nutzkurz, 
                          self.combo_vergleich_typ, self.combo_such_beginn, 
                          self.combo_id_zeilen_typ]:
                combo['values'] = felder
            
            # Standard-Werte setzen basierend auf Namen
            if 'QuellWort' in felder:
                self.combo_quell_wort.set('QuellWort')
            if 'TypNutzkurz' in felder:
                self.combo_typ_nutzkurz.set('TypNutzkurz')
            if 'Vergleich_Ganz_Teil' in felder:
                self.combo_vergleich_typ.set('Vergleich_Ganz_Teil')
            if 'SuchBeginnTeilstring' in felder:
                self.combo_such_beginn.set('SuchBeginnTeilstring')
            if 'IDZeilenTyp' in felder:
                self.combo_id_zeilen_typ.set('IDZeilenTyp')
                
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Laden der Quell-Felder:\n{str(e)}")
    
    def ziel_felder_laden(self):
        """Lädt die Felder der Ziel-Tabelle"""
        tabelle = self.combo_ziel_tabelle.get()
        if not tabelle:
            return
        
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute(f'PRAGMA table_info({tabelle})')
            felder_info = cursor.fetchall()
            felder = [info[1] for info in felder_info]
            conn.close()
            
            self.combo_ziel_inhalt['values'] = felder
            self.combo_ziel_typ['values'] = felder
            
            # Standard-Werte setzen
            if 'Inhalt' in felder:
                self.combo_ziel_inhalt.set('Inhalt')
            if 'Typ' in felder:
                self.combo_ziel_typ.set('Typ')
                
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Laden der Ziel-Felder:\n{str(e)}")
    
    def ziel_tabelle_anzeigen(self):
        """Zeigt die Ziel-Tabelle in einem neuen Fenster an"""
        ziel_tabelle = self.combo_ziel_tabelle.get()
        if not ziel_tabelle:
            messagebox.showerror("Fehler", "Bitte wählen Sie eine Ziel-Tabelle aus!")
            return
        
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Prüfen ob Tabelle existiert
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (ziel_tabelle,))
            if not cursor.fetchone():
                messagebox.showerror("Fehler", f"Tabelle '{ziel_tabelle}' nicht gefunden!")
                conn.close()
                return
            
            # Alle Daten abrufen
            cursor.execute(f'SELECT * FROM {ziel_tabelle} ORDER BY id DESC LIMIT 1000')
            daten = cursor.fetchall()
            
            # Spalten-Info abrufen
            cursor.execute(f'PRAGMA table_info({ziel_tabelle})')
            spalten_info = cursor.fetchall()
            spalten_namen = [info[1] for info in spalten_info]
            
            # Anzahl Datensätze
            cursor.execute(f'SELECT COUNT(*) FROM {ziel_tabelle}')
            gesamt_anzahl = cursor.fetchone()[0]
            
            conn.close()
            
            # Neues Fenster erstellen
            tabelle_window = tk.Toplevel(self.root)
            tabelle_window.title(f"Ziel-Tabelle: {ziel_tabelle}")
            tabelle_window.geometry("1200x700")
            
            # Titel
            titel_frame = tk.Frame(tabelle_window, bg="#e8f5e8", pady=10)
            titel_frame.pack(fill=tk.X)
            tk.Label(titel_frame, text=f"Tabelle: {ziel_tabelle}", 
                    font=("Arial", 14, "bold"), bg="#e8f5e8").pack()
            tk.Label(titel_frame, text=f"Gesamt: {gesamt_anzahl} Datensätze (Angezeigt: {len(daten)})", 
                    font=("Arial", 10), bg="#e8f5e8").pack()
            
            # Treeview Frame
            tree_frame = tk.Frame(tabelle_window)
            tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Scrollbars
            v_scrollbar = tk.Scrollbar(tree_frame, orient="vertical")
            v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            h_scrollbar = tk.Scrollbar(tree_frame, orient="horizontal")
            h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
            
            # Treeview
            tree = ttk.Treeview(tree_frame, 
                               yscrollcommand=v_scrollbar.set, 
                               xscrollcommand=h_scrollbar.set)
            tree.pack(fill=tk.BOTH, expand=True)
            
            v_scrollbar.config(command=tree.yview)
            h_scrollbar.config(command=tree.xview)
            
            # Spalten konfigurieren
            tree["columns"] = spalten_namen
            tree["show"] = "headings"
            
            # Spaltenüberschriften mit Sortierung
            for spalte in spalten_namen:
                tree.heading(spalte, text=spalte, 
                           command=lambda col=spalte: self.spalte_sortieren(tree, col, False))
                # Spaltenbreite anpassen
                if spalte.lower() in ['id']:
                    tree.column(spalte, width=60, anchor=tk.W)
                elif spalte.lower() in ['typ']:
                    tree.column(spalte, width=100, anchor=tk.W)
                else:
                    tree.column(spalte, width=200, anchor=tk.W)
            
            # Speichere ursprüngliche Daten für Sortierung
            self.original_daten = daten
            self.original_spalten = spalten_namen[:]
            self.aktuelle_spalten = spalten_namen[:]
            self.sort_reverse = {}  # Tracking für Sortierrichtung
            
            # Daten einfügen
            self.daten_in_tree_einfuegen(tree, daten)
            
            # Drag & Drop für Spalten aktivieren
            self.drag_drop_aktivieren(tree)
            
            # Button Frame
            btn_frame = tk.Frame(tabelle_window)
            btn_frame.pack(fill=tk.X, padx=10, pady=5)
            
            # Aktualisieren Button
            btn_refresh = tk.Button(btn_frame, text="🔄 Aktualisieren", 
                                   command=lambda: self.tabelle_aktualisieren(tree, ziel_tabelle, spalten_namen, titel_frame),
                                   bg="#17a2b8", fg="white", font=("Arial", 10))
            btn_refresh.pack(side=tk.LEFT, padx=(0, 5))
            
            # Export Button
            btn_export = tk.Button(btn_frame, text="📄 TXT Export", 
                                  command=lambda: self.tabelle_exportieren(ziel_tabelle, spalten_namen),
                                  bg="#fd7e14", fg="white", font=("Arial", 10))
            btn_export.pack(side=tk.LEFT, padx=(0, 5))
            
            # Schließen Button
            btn_close = tk.Button(btn_frame, text="❌ Schließen", 
                                 command=tabelle_window.destroy,
                                 bg="#dc3545", fg="white", font=("Arial", 10))
            btn_close.pack(side=tk.RIGHT)
            
        except Exception as e:
            messagebox.showerror("Anzeige-Fehler", f"Fehler beim Anzeigen der Tabelle:\n{str(e)}")
    
    def tabelle_aktualisieren(self, tree, tabelle_name, spalten_namen, titel_frame):
        """Aktualisiert die Tabellenanzeige"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Neue Daten abrufen
            cursor.execute(f'SELECT * FROM {tabelle_name} ORDER BY id DESC LIMIT 1000')
            daten = cursor.fetchall()
            
            # Anzahl Datensätze
            cursor.execute(f'SELECT COUNT(*) FROM {tabelle_name}')
            gesamt_anzahl = cursor.fetchone()[0]
            
            conn.close()
            
            # Treeview leeren
            for item in tree.get_children():
                tree.delete(item)
            
            # Neue Daten einfügen
            self.daten_in_tree_einfuegen(tree, daten)
            
            # Original-Daten aktualisieren für Sortierung
            self.original_daten = daten
            
            # Titel aktualisieren
            for widget in titel_frame.winfo_children():
                if isinstance(widget, tk.Label) and "Gesamt:" in widget.cget("text"):
                    widget.config(text=f"Gesamt: {gesamt_anzahl} Datensätze (Angezeigt: {len(daten)})")
                    break
            
        except Exception as e:
            messagebox.showerror("Aktualisierung-Fehler", f"Fehler beim Aktualisieren:\n{str(e)}")
    
    def daten_in_tree_einfuegen(self, tree, daten):
        """Fügt Daten in den Treeview ein mit Textkürzung"""
        for row in daten:
            display_row = []
            for item in row:
                if item is None:
                    display_row.append("")
                else:
                    item_str = str(item)
                    if len(item_str) > 100:
                        display_row.append(item_str[:97] + "...")
                    else:
                        display_row.append(item_str)
            tree.insert("", tk.END, values=display_row)
    
    def spalte_sortieren(self, tree, spalte, reverse):
        """Sortiert den Treeview nach der angegebenen Spalte"""
        try:
            # Spaltenindex finden
            spalten_liste = list(tree["columns"])
            if spalte not in spalten_liste:
                return
            
            spalten_index = spalten_liste.index(spalte)
            
            # Aktuelle Sortierrichtung umkehren
            if spalte in self.sort_reverse:
                self.sort_reverse[spalte] = not self.sort_reverse[spalte]
            else:
                self.sort_reverse[spalte] = reverse
            
            # Daten mit ursprünglichen Werten sortieren
            def sort_key(row):
                value = row[spalten_index]
                if value is None:
                    return ""
                # Versuche numerische Sortierung
                try:
                    return float(str(value))
                except (ValueError, TypeError):
                    return str(value).lower()
            
            sortierte_daten = sorted(self.original_daten, 
                                   key=sort_key, 
                                   reverse=self.sort_reverse[spalte])
            
            # Treeview leeren und neu befüllen
            for item in tree.get_children():
                tree.delete(item)
            
            self.daten_in_tree_einfuegen(tree, sortierte_daten)
            
            # Spaltenüberschrift mit Sortier-Indikator aktualisieren
            for col in spalten_liste:
                if col == spalte:
                    pfeil = " ▼" if self.sort_reverse[spalte] else " ▲"
                    tree.heading(col, text=f"{col}{pfeil}")
                else:
                    tree.heading(col, text=col)
                    
        except Exception as e:
            messagebox.showerror("Sortier-Fehler", f"Fehler beim Sortieren:\n{str(e)}")
    
    def drag_drop_aktivieren(self, tree):
        """Aktiviert Drag & Drop für Spaltenverschiebung"""
        self.drag_data = {"spalte": None, "x": 0}
        
        def on_drag_start(event):
            # Ermittle angeklickte Spalte
            region = tree.identify_region(event.x, event.y)
            if region == "heading":
                spalte = tree.identify_column(event.x)
                try:
                    spalte_index = int(spalte.replace('#', '')) - 1
                    if 0 <= spalte_index < len(self.aktuelle_spalten):
                        self.drag_data["spalte"] = self.aktuelle_spalten[spalte_index]
                        self.drag_data["x"] = event.x
                        tree.config(cursor="fleur")
                except:
                    pass
        
        def on_drag_motion(event):
            if self.drag_data["spalte"]:
                tree.config(cursor="fleur")
        
        def on_drag_end(event):
            if self.drag_data["spalte"]:
                # Ziel-Spalte ermitteln
                region = tree.identify_region(event.x, event.y)
                if region == "heading":
                    ziel_spalte = tree.identify_column(event.x)
                    try:
                        ziel_index = int(ziel_spalte.replace('#', '')) - 1
                        if 0 <= ziel_index < len(self.aktuelle_spalten):
                            ziel_spalte_name = self.aktuelle_spalten[ziel_index]
                            self.spalten_verschieben(tree, self.drag_data["spalte"], ziel_spalte_name)
                    except:
                        pass
                
                tree.config(cursor="")
                self.drag_data = {"spalte": None, "x": 0}
        
        # Events binden
        tree.bind("<Button-1>", on_drag_start)
        tree.bind("<B1-Motion>", on_drag_motion)
        tree.bind("<ButtonRelease-1>", on_drag_end)
    
    def spalten_verschieben(self, tree, quell_spalte, ziel_spalte):
        """Verschiebt eine Spalte an eine neue Position"""
        try:
            if quell_spalte == ziel_spalte:
                return
            
            # Aktuelle Positionen ermitteln
            quell_index = self.aktuelle_spalten.index(quell_spalte)
            ziel_index = self.aktuelle_spalten.index(ziel_spalte)
            
            # Spalte verschieben in der Liste
            spalte = self.aktuelle_spalten.pop(quell_index)
            self.aktuelle_spalten.insert(ziel_index, spalte)
            
            # Treeview neu konfigurieren
            tree.config(columns=self.aktuelle_spalten)
            
            # Spaltenüberschriften neu setzen
            for i, spalte in enumerate(self.aktuelle_spalten):
                tree.heading(f"#{i+1}", text=spalte,
                           command=lambda col=spalte: self.spalte_sortieren(tree, col, False))
                
                # Spaltenbreite neu setzen
                if spalte.lower() in ['id']:
                    tree.column(f"#{i+1}", width=60, anchor=tk.W)
                elif spalte.lower() in ['typ']:
                    tree.column(f"#{i+1}", width=100, anchor=tk.W)
                else:
                    tree.column(f"#{i+1}", width=200, anchor=tk.W)
            
            # Daten in neuer Spaltenreihenfolge anzeigen
            for item in tree.get_children():
                tree.delete(item)
            
            # Original-Daten in neuer Spaltenreihenfolge sortieren
            if hasattr(self, 'original_spalten'):
                original_indices = []
                for spalte in self.aktuelle_spalten:
                    original_indices.append(self.original_spalten.index(spalte))
                
                neu_sortierte_daten = []
                for row in self.original_daten:
                    neue_row = [row[i] for i in original_indices]
                    neu_sortierte_daten.append(neue_row)
                
                self.daten_in_tree_einfuegen(tree, neu_sortierte_daten)
            else:
                self.daten_in_tree_einfuegen(tree, self.original_daten)
                
        except Exception as e:
            messagebox.showerror("Verschiebe-Fehler", f"Fehler beim Verschieben der Spalte:\n{str(e)}")
    
    def tabelle_exportieren(self, tabelle_name, spalten_namen):
        """Exportiert die Tabelle als TXT-Datei mit Semikolon-Trennung"""
        try:
            from tkinter import filedialog
            
            # Datei-Dialog für Speicherort
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            standard_name = f"{tabelle_name}_export_{timestamp}.txt"
            
            datei_pfad = filedialog.asksaveasfilename(
                title="TXT Export speichern unter",
                defaultextension=".txt",
                initialfile=standard_name,
                filetypes=[
                    ("Text-Dateien", "*.txt"),
                    ("CSV-Dateien", "*.csv"),
                    ("Alle Dateien", "*.*")
                ]
            )
            
            if not datei_pfad:
                return
            
            # Daten aus Datenbank holen
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Alle Daten exportieren (nicht nur die ersten 1000)
            cursor.execute(f'SELECT * FROM {tabelle_name}')
            alle_daten = cursor.fetchall()
            
            cursor.execute(f'SELECT COUNT(*) FROM {tabelle_name}')
            gesamt_anzahl = cursor.fetchone()[0]
            
            conn.close()
            
            # TXT-Datei schreiben
            with open(datei_pfad, 'w', encoding='utf-8', newline='') as datei:
                # Kopfzeile schreiben
                datei.write(';'.join(spalten_namen) + '\n')
                
                # Datenzeilen schreiben
                for row in alle_daten:
                    # None-Werte durch leere Strings ersetzen und Semikolons in Daten escapen
                    bereinigte_row = []
                    for item in row:
                        if item is None:
                            bereinigte_row.append("")
                        else:
                            # Semikolons und Zeilentrenner in den Daten escapen
                            item_str = str(item).replace(';', ',').replace('\n', ' ').replace('\r', '')
                            bereinigte_row.append(item_str)
                    
                    datei.write(';'.join(bereinigte_row) + '\n')
            
            # Erfolg-Meldung
            messagebox.showinfo("Export erfolgreich", 
                               f"Tabelle '{tabelle_name}' wurde exportiert!\n\n"
                               f"Datei: {datei_pfad}\n"
                               f"Datensätze: {gesamt_anzahl}\n"
                               f"Spalten: {len(spalten_namen)}\n"
                               f"Format: Semikolon-getrennt (UTF-8)")
            
            # Protokoll-Eintrag
            if hasattr(self, 'txt_protokoll'):
                self.txt_protokoll.insert(tk.END, 
                    f"[{datetime.now().strftime('%H:%M:%S')}] Export erstellt: {standard_name} ({gesamt_anzahl} Zeilen)\n")
            
            self.status_label.config(text=f"Export erstellt: {standard_name}")
            
        except Exception as e:
            messagebox.showerror("Export-Fehler", f"Fehler beim Exportieren der Tabelle:\n{str(e)}")

    def backup_erstellen(self):
        """Erstellt ein Backup der Ziel-Tabelle"""
        ziel_tabelle = self.combo_ziel_tabelle.get()
        if not ziel_tabelle:
            messagebox.showerror("Fehler", "Bitte wählen Sie eine Ziel-Tabelle aus!")
            return
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{ziel_tabelle}_backup_{timestamp}.db"
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            # Datenbank kopieren
            shutil.copy2(self.db_name, backup_path)
            
            messagebox.showinfo("Backup erstellt", 
                               f"Backup wurde erstellt:\n{backup_path}")
            
            self.txt_protokoll.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Backup erstellt: {backup_filename}\n")
            self.status_label.config(text=f"Backup erstellt: {backup_filename}")
            
        except Exception as e:
            messagebox.showerror("Backup-Fehler", f"Fehler beim Erstellen des Backups:\n{str(e)}")
    
    def abgleich_starten(self):
        """Startet den Tabellen-Abgleich"""
        # Validierung
        if not self.eingaben_validieren():
            return
        
        try:
            self.btn_start.config(state=tk.DISABLED)
            self.txt_protokoll.delete(1.0, tk.END)
            
            # Parameter abrufen
            quell_tabelle = self.combo_quell_tabelle.get()
            ziel_tabelle = self.combo_ziel_tabelle.get()
            
            quell_wort_feld = self.combo_quell_wort.get()
            typ_nutzkurz_feld = self.combo_typ_nutzkurz.get()
            vergleich_typ_feld = self.combo_vergleich_typ.get()
            such_beginn_feld = self.combo_such_beginn.get()
            id_zeilen_typ_feld = self.combo_id_zeilen_typ.get()
            
            ziel_inhalt_feld = self.combo_ziel_inhalt.get()
            ziel_typ_feld = self.combo_ziel_typ.get()
            
            self.txt_protokoll.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] Abgleich gestartet\n")
            self.txt_protokoll.insert(tk.END, f"Quell-Tabelle: {quell_tabelle}\n")
            self.txt_protokoll.insert(tk.END, f"Ziel-Tabelle: {ziel_tabelle}\n\n")
            
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Quell-Regeln laden (sortiert nach IDZeilenTyp)
            cursor.execute(f'''
                SELECT "{quell_wort_feld}", "{typ_nutzkurz_feld}", 
                       "{vergleich_typ_feld}", "{such_beginn_feld}", "{id_zeilen_typ_feld}"
                FROM {quell_tabelle} 
                ORDER BY "{id_zeilen_typ_feld}" ASC
            ''')
            quell_regeln = cursor.fetchall()
            
            if not quell_regeln:
                messagebox.showwarning("Keine Regeln", f"Keine Regeln in Tabelle '{quell_tabelle}' gefunden!")
                conn.close()
                return
            
            # Ziel-Daten laden
            cursor.execute(f'SELECT id, "{ziel_inhalt_feld}" FROM {ziel_tabelle}')
            ziel_daten = cursor.fetchall()
            
            if not ziel_daten:
                messagebox.showwarning("Keine Daten", f"Keine Daten in Tabelle '{ziel_tabelle}' gefunden!")
                conn.close()
                return
            
            self.progress['maximum'] = len(ziel_daten)
            
            treffer_count = 0
            verarbeitete_count = 0
            
            # Für jede Zeile in der Ziel-Tabelle
            for ziel_id, ziel_inhalt in ziel_daten:
                if ziel_inhalt is None:
                    ziel_inhalt = ""
                else:
                    ziel_inhalt = str(ziel_inhalt)
                
                # Durch alle Regeln gehen (aufsteigend nach IDZeilenTyp)
                regel_gefunden = False
                for quell_wort, typ_nutzkurz, vergleich_typ, such_beginn, id_zeilen_typ in quell_regeln:
                    if regel_gefunden:
                        break
                    
                    if quell_wort is None:
                        continue
                    
                    quell_wort = str(quell_wort)
                    vergleich_typ = str(vergleich_typ).lower() if vergleich_typ else "g"
                    such_beginn = str(such_beginn) if such_beginn else "0"
                    
                    # Vergleich durchführen
                    ist_treffer = False
                    
                    if vergleich_typ == "g":  # Ganz-Vergleich (1:1)
                        ist_treffer = (ziel_inhalt == quell_wort)
                    elif vergleich_typ == "t":  # Teil-Vergleich
                        if such_beginn == "1":  # Am Anfang
                            ist_treffer = ziel_inhalt.startswith(quell_wort)
                        else:  # Position im String (0 = irgendwo)
                            ist_treffer = (quell_wort in ziel_inhalt)
                    
                    if ist_treffer:
                        # Typ-Feld aktualisieren
                        cursor.execute(f'''
                            UPDATE {ziel_tabelle} 
                            SET "{ziel_typ_feld}" = ? 
                            WHERE id = ?
                        ''', (typ_nutzkurz, ziel_id))
                        
                        treffer_count += 1
                        regel_gefunden = True
                        
                        self.txt_protokoll.insert(tk.END, 
                            f"Treffer #{treffer_count}: ID {ziel_id} -> '{typ_nutzkurz}' (Regel: {id_zeilen_typ})\n")
                
                verarbeitete_count += 1
                self.progress['value'] = verarbeitete_count
                
                if verarbeitete_count % 100 == 0:
                    self.lbl_status.config(text=f"Verarbeitet: {verarbeitete_count}/{len(ziel_daten)} - Treffer: {treffer_count}")
                    self.root.update()
            
            conn.commit()
            conn.close()
            
            # Abschluss
            self.txt_protokoll.insert(tk.END, f"\n=== ABGLEICH ABGESCHLOSSEN ===\n")
            self.txt_protokoll.insert(tk.END, f"Verarbeitete Zeilen: {len(ziel_daten)}\n")
            self.txt_protokoll.insert(tk.END, f"Treffer gefunden: {treffer_count}\n")
            self.txt_protokoll.insert(tk.END, f"Abgeschlossen: {datetime.now().strftime('%H:%M:%S')}\n")
            
            self.lbl_status.config(text=f"Fertig: {treffer_count} Treffer bei {len(ziel_daten)} Zeilen")
            self.status_label.config(text=f"Abgleich abgeschlossen: {treffer_count} Treffer")
            
            messagebox.showinfo("Abgleich abgeschlossen", 
                               f"Abgleich erfolgreich!\n\nVerarbeitet: {len(ziel_daten)} Zeilen\nTreffer: {treffer_count}")
            
        except Exception as e:
            messagebox.showerror("Abgleich-Fehler", f"Fehler beim Abgleich:\n{str(e)}")
            self.txt_protokoll.insert(tk.END, f"\nFEHLER: {str(e)}\n")
        finally:
            self.btn_start.config(state=tk.NORMAL)
            self.progress['value'] = 0
    
    def eingaben_validieren(self):
        """Validiert die Eingaben vor dem Start"""
        fehlende = []
        
        if not self.combo_quell_tabelle.get():
            fehlende.append("Quell-Tabelle")
        if not self.combo_ziel_tabelle.get():
            fehlende.append("Ziel-Tabelle")
        if not self.combo_quell_wort.get():
            fehlende.append("QuellWort Feld")
        if not self.combo_typ_nutzkurz.get():
            fehlende.append("TypNutzkurz Feld")
        if not self.combo_vergleich_typ.get():
            fehlende.append("Vergleich_Ganz_Teil Feld")
        if not self.combo_ziel_inhalt.get():
            fehlende.append("Ziel Inhalt Feld")
        if not self.combo_ziel_typ.get():
            fehlende.append("Ziel Typ Feld")
        
        if fehlende:
            messagebox.showerror("Unvollständige Eingaben", 
                               f"Bitte füllen Sie folgende Felder aus:\n\n" + 
                               "\n".join(f"• {feld}" for feld in fehlende))
            return False
        
        return True


if __name__ == "__main__":
    root = tk.Tk()
    app = TabellenAbgleichApp(root)
    root.mainloop()