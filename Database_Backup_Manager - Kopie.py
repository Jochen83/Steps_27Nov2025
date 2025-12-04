import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sqlite3
import os
from datetime import datetime
import shutil

# Datenbank Backup & Restore Manager für regatta_unified.db
# Erstellt am 03.12.2025

class DatabaseBackupManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Datenbank Backup & Restore Manager")
        self.root.geometry("1000x700")
        
        # Variablen
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(script_dir, "regatta_unified.db")
        self.selected_table = None
        
        # GUI erstellen
        self.gui_erstellen()
        
        # Initial Tabellen laden
        self.tabellen_laden()
    
    def gui_erstellen(self):
        """Erstellt die GUI-Elemente"""
        
        # Titel
        titel_frame = tk.Frame(self.root, bg="#2c3e50", pady=15)
        titel_frame.pack(fill=tk.X)
        
        tk.Label(titel_frame, text="🗄️ Datenbank Backup & Restore Manager", 
                 font=("Arial", 18, "bold"), fg="white", bg="#2c3e50").pack()
        tk.Label(titel_frame, text="Backup, Wiederherstellung und Basis-Kopien von Datenbanktabellen", 
                 font=("Arial", 11), fg="#bdc3c7", bg="#2c3e50").pack()
        
        # Info über Datenbank
        info_frame = tk.Frame(self.root, bg="#f8f9fa", pady=8)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(info_frame, text="📁 Datenbank:", font=("Arial", 10, "bold"), bg="#f8f9fa").pack(side=tk.LEFT, padx=10)
        self.lbl_db_path = tk.Label(info_frame, text=self.db_path, 
                                   font=("Arial", 9), bg="#f8f9fa", fg="#0066cc")
        self.lbl_db_path.pack(side=tk.LEFT, padx=5)
        
        # Hauptcontainer
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # Linke Seite - Tabellenliste
        left_frame = tk.LabelFrame(main_frame, text="Verfügbare Tabellen", font=("Arial", 12, "bold"))
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Refresh Button
        refresh_frame = tk.Frame(left_frame)
        refresh_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(refresh_frame, text="🔄 Aktualisieren", command=self.tabellen_laden,
                  bg="#17a2b8", fg="white", font=("Arial", 9, "bold")).pack(side=tk.LEFT)
        
        self.lbl_table_count = tk.Label(refresh_frame, text="", font=("Arial", 9), fg="gray")
        self.lbl_table_count.pack(side=tk.RIGHT)
        
        # Treeview für Tabellen
        tree_frame = tk.Frame(left_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.table_tree = ttk.Treeview(tree_frame, columns=("Tabelle", "Datensätze", "Typ"), show="headings", height=20)
        
        # Spalten konfigurieren
        self.table_tree.heading("Tabelle", text="Tabellen-Name")
        self.table_tree.heading("Datensätze", text="Anzahl Datensätze")
        self.table_tree.heading("Typ", text="Typ")
        
        self.table_tree.column("Tabelle", width=250, anchor="w")
        self.table_tree.column("Datensätze", width=120, anchor="center")
        self.table_tree.column("Typ", width=100, anchor="center")
        
        # Scrollbar
        table_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.table_tree.yview)
        self.table_tree.configure(yscrollcommand=table_scrollbar.set)
        
        self.table_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        table_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Event für Auswahl
        self.table_tree.bind('<<TreeviewSelect>>', self.tabelle_auswaehlen)
        
        # Rechte Seite - Aktionen
        right_frame = tk.LabelFrame(main_frame, text="Aktionen", font=("Arial", 12, "bold"))
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        
        # Ausgewählte Tabelle anzeigen
        selection_frame = tk.Frame(right_frame)
        selection_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(selection_frame, text="Ausgewählte Tabelle:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.lbl_selected = tk.Label(selection_frame, text="Keine Tabelle ausgewählt", 
                                    font=("Arial", 10), fg="gray", bg="#f8f9fa", pady=5)
        self.lbl_selected.pack(fill=tk.X, pady=5)
        
        # Backup Buttons
        backup_frame = tk.LabelFrame(right_frame, text="Backup Aktionen", font=("Arial", 11, "bold"))
        backup_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.btn_create_backup = tk.Button(backup_frame, text="💾 Backup erstellen\n(_bak + Zeitstempel)", 
                                          command=self.backup_erstellen, state=tk.DISABLED,
                                          bg="#28a745", fg="white", font=("Arial", 10, "bold"), 
                                          height=3, wraplength=150, justify=tk.CENTER)
        self.btn_create_backup.pack(fill=tk.X, padx=10, pady=5)
        
        self.btn_restore_backup = tk.Button(backup_frame, text="↩️ Aus Backup wiederherstellen", 
                                           command=self.backup_wiederherstellen, state=tk.DISABLED,
                                           bg="#ffc107", fg="black", font=("Arial", 10, "bold"), 
                                           height=2, wraplength=150, justify=tk.CENTER)
        self.btn_restore_backup.pack(fill=tk.X, padx=10, pady=5)
        
        # Base Buttons
        base_frame = tk.LabelFrame(right_frame, text="Basis-Kopie Aktionen", font=("Arial", 11, "bold"))
        base_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.btn_create_base = tk.Button(base_frame, text="📋 Basis-Kopie erstellen\n(_base + Zeitstempel)", 
                                        command=self.basis_kopie_erstellen, state=tk.DISABLED,
                                        bg="#17a2b8", fg="white", font=("Arial", 10, "bold"), 
                                        height=3, wraplength=150, justify=tk.CENTER)
        self.btn_create_base.pack(fill=tk.X, padx=10, pady=5)
        
        # Spezial-Aktionen
        special_frame = tk.LabelFrame(right_frame, text="Spezial-Aktionen", font=("Arial", 11, "bold"))
        special_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.btn_show_backups = tk.Button(special_frame, text="📋 Verfügbare Backups anzeigen", 
                                         command=self.backups_anzeigen, state=tk.DISABLED,
                                         bg="#6f42c1", fg="white", font=("Arial", 9, "bold"), 
                                         height=2, wraplength=150, justify=tk.CENTER)
        self.btn_show_backups.pack(fill=tk.X, padx=10, pady=5)
        
        self.btn_show_table = tk.Button(special_frame, text="📋 Tabelle anzeigen\n(sortierbar)", 
                                        command=self.tabelle_anzeigen, state=tk.DISABLED,
                                        bg="#17a2b8", fg="white", font=("Arial", 9, "bold"), 
                                        height=3, wraplength=150, justify=tk.CENTER)
        self.btn_show_table.pack(fill=tk.X, padx=10, pady=5)
        
        self.btn_append_to_base = tk.Button(special_frame, text="🔗 An Base-Tabelle anhängen", 
                                           command=self.an_base_anhaengen, state=tk.DISABLED,
                                           bg="#28a745", fg="white", font=("Arial", 9, "bold"), 
                                           height=2, wraplength=150, justify=tk.CENTER)
        self.btn_append_to_base.pack(fill=tk.X, padx=10, pady=5)
        
        self.btn_delete_table = tk.Button(special_frame, text="🗑️ Tabelle löschen\n(Vorsicht!)", 
                                         command=self.tabelle_loeschen, state=tk.DISABLED,
                                         bg="#dc3545", fg="white", font=("Arial", 9, "bold"), 
                                         height=3, wraplength=150, justify=tk.CENTER)
        self.btn_delete_table.pack(fill=tk.X, padx=10, pady=5)
        
        # Log-Bereich
        log_frame = tk.Frame(self.root)
        log_frame.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        tk.Label(log_frame, text="Aktivitäts-Log:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.txt_log = scrolledtext.ScrolledText(log_frame, height=8, font=("Courier", 9))
        self.txt_log.pack(fill=tk.X)
        
        # Statusleiste
        self.status_label = tk.Label(self.root, text="Bereit", bg="#e0e0e0", anchor=tk.W, font=("Arial", 9))
        self.status_label.pack(fill=tk.X, side=tk.BOTTOM)
    
    def log(self, message):
        """Fügt eine Nachricht zum Log hinzu"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.txt_log.insert(tk.END, f"[{timestamp}] {message}\n")
        self.txt_log.see(tk.END)
        self.root.update()
    
    def get_timestamp(self):
        """Erstellt Zeitstempel im Format JJMMTT_SSMM"""
        now = datetime.now()
        return now.strftime("%y%m%d_%H%M")
    
    def tabellen_laden(self):
        """Lädt alle Tabellen aus der Datenbank"""
        if not os.path.exists(self.db_path):
            messagebox.showerror("Fehler", f"Datenbank nicht gefunden:\\n{self.db_path}")
            self.status_label.config(text="Datenbank nicht gefunden")
            return
        
        try:
            # Treeview leeren
            for item in self.table_tree.get_children():
                self.table_tree.delete(item)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Alle Tabellen abrufen
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            tables = cursor.fetchall()
            
            table_count = 0
            backup_count = 0
            base_count = 0
            normal_count = 0
            
            for (table_name,) in tables:
                # Anzahl Datensätze ermitteln
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM `{table_name}`")
                    record_count = cursor.fetchone()[0]
                except:
                    record_count = "N/A"
                
                # Typ bestimmen
                if "_bak" in table_name:
                    table_type = "Backup"
                    backup_count += 1
                elif "_base" in table_name:
                    table_type = "Basis"
                    base_count += 1
                else:
                    table_type = "Normal"
                    normal_count += 1
                
                # In Treeview einfügen
                self.table_tree.insert("", "end", values=(table_name, record_count, table_type))
                table_count += 1
            
            conn.close()
            
            self.lbl_table_count.config(text=f"Gesamt: {table_count} (Normal: {normal_count}, Backup: {backup_count}, Basis: {base_count})")
            self.status_label.config(text=f"{table_count} Tabellen geladen")
            self.log(f"✅ {table_count} Tabellen geladen (Normal: {normal_count}, Backup: {backup_count}, Basis: {base_count})")
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Laden der Tabellen:\\n{str(e)}")
            self.status_label.config(text="Fehler beim Laden")
            self.log(f"❌ Fehler beim Laden der Tabellen: {str(e)}")
    
    def tabelle_auswaehlen(self, event):
        """Wird aufgerufen wenn eine Tabelle ausgewählt wird"""
        selection = self.table_tree.selection()
        if not selection:
            return
        
        item = self.table_tree.item(selection[0])
        table_name = item['values'][0]
        record_count = item['values'][1]
        table_type = item['values'][2]
        
        self.selected_table = table_name
        self.lbl_selected.config(text=f"{table_name}\n({record_count} Datensätze, {table_type})")
        
        # Buttons aktivieren
        self.btn_create_backup.config(state=tk.NORMAL)
        self.btn_restore_backup.config(state=tk.NORMAL)
        self.btn_create_base.config(state=tk.NORMAL)
        self.btn_show_backups.config(state=tk.NORMAL)
        self.btn_show_table.config(state=tk.NORMAL)
        self.btn_append_to_base.config(state=tk.NORMAL)
        self.btn_delete_table.config(state=tk.NORMAL)
        
        self.status_label.config(text=f"Tabelle '{table_name}' ausgewählt")
    
    def backup_erstellen(self):
        """Erstellt ein Backup der ausgewählten Tabelle"""
        if not self.selected_table:
            messagebox.showwarning("Keine Auswahl", "Bitte wählen Sie eine Tabelle aus.")
            return
        
        try:
            timestamp = self.get_timestamp()
            backup_name = f"{self.selected_table}_bak{timestamp}"
            
            # Bestätigung
            antwort = messagebox.askyesno("Backup erstellen", 
                                         f"Backup erstellen?\\n\\nOriginal: {self.selected_table}\\nBackup: {backup_name}")
            if not antwort:
                return
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Prüfen ob Backup bereits existiert
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (backup_name,))
            if cursor.fetchone():
                antwort2 = messagebox.askyesno("Backup überschreiben", 
                                              f"Backup '{backup_name}' existiert bereits.\\nÜberschreiben?")
                if not antwort2:
                    conn.close()
                    return
                
                cursor.execute(f"DROP TABLE `{backup_name}`")
            
            # Tabelle kopieren
            cursor.execute(f"CREATE TABLE `{backup_name}` AS SELECT * FROM `{self.selected_table}`")
            
            # Datensätze zählen
            cursor.execute(f"SELECT COUNT(*) FROM `{backup_name}`")
            backup_count = cursor.fetchone()[0]
            
            conn.commit()
            conn.close()
            
            self.log(f"✅ Backup erstellt: {backup_name} ({backup_count} Datensätze)")
            self.status_label.config(text=f"Backup '{backup_name}' erstellt")
            
            # Tabellenliste aktualisieren
            self.tabellen_laden()
            
            messagebox.showinfo("Backup erstellt", f"Backup erfolgreich erstellt:\\n{backup_name}\\n\\n{backup_count} Datensätze kopiert")
            
        except Exception as e:
            messagebox.showerror("Backup-Fehler", f"Fehler beim Erstellen des Backups:\\n{str(e)}")
            self.log(f"❌ Backup-Fehler: {str(e)}")
    
    def backup_wiederherstellen(self):
        """Stellt eine Tabelle aus einem Backup wieder her"""
        if not self.selected_table:
            messagebox.showwarning("Keine Auswahl", "Bitte wählen Sie eine Tabelle aus.")
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Verfügbare Backups für diese Tabelle finden
            base_name = self.selected_table.split('_bak')[0]  # Basis-Tabellenname
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE ? ORDER BY name DESC", 
                          (f"{base_name}_bak%",))
            backups = cursor.fetchall()
            
            conn.close()
            
            if not backups:
                messagebox.showinfo("Keine Backups", f"Keine Backups für Tabelle '{base_name}' gefunden.")
                return
            
            # Backup auswählen
            backup_window = tk.Toplevel(self.root)
            backup_window.title("Backup auswählen")
            backup_window.geometry("500x400")
            backup_window.transient(self.root)
            backup_window.grab_set()
            
            tk.Label(backup_window, text=f"Verfügbare Backups für '{base_name}':", 
                     font=("Arial", 12, "bold")).pack(pady=10)
            
            backup_listbox = tk.Listbox(backup_window, font=("Courier", 10))
            backup_listbox.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            
            for (backup_name,) in backups:
                backup_listbox.insert(tk.END, backup_name)
            
            selected_backup = [None]
            
            def restore_selected():
                selection = backup_listbox.curselection()
                if not selection:
                    messagebox.showwarning("Keine Auswahl", "Bitte wählen Sie ein Backup aus.")
                    return
                
                selected_backup[0] = backup_listbox.get(selection[0])
                backup_window.destroy()
            
            def cancel_restore():
                backup_window.destroy()
            
            button_frame = tk.Frame(backup_window)
            button_frame.pack(fill=tk.X, padx=20, pady=10)
            
            tk.Button(button_frame, text="↩️ Wiederherstellen", command=restore_selected,
                      bg="#28a745", fg="white", font=("Arial", 11, "bold")).pack(side=tk.LEFT, padx=(0, 10))
            
            tk.Button(button_frame, text="❌ Abbrechen", command=cancel_restore,
                      bg="#6c757d", fg="white", font=("Arial", 11, "bold")).pack(side=tk.LEFT)
            
            backup_window.wait_window()
            
            if not selected_backup[0]:
                return
            
            # Wiederherstellung durchführen
            antwort = messagebox.askyesno("Wiederherstellung bestätigen",
                                         f"Tabelle '{base_name}' aus Backup '{selected_backup[0]}' wiederherstellen?\\n\\n"
                                         f"ACHTUNG: Die aktuelle Tabelle '{base_name}' wird überschrieben!")
            
            if not antwort:
                return
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Original-Tabelle löschen falls vorhanden
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (base_name,))
            if cursor.fetchone():
                cursor.execute(f"DROP TABLE `{base_name}`")
            
            # Aus Backup wiederherstellen
            cursor.execute(f"CREATE TABLE `{base_name}` AS SELECT * FROM `{selected_backup[0]}`")
            
            # Datensätze zählen
            cursor.execute(f"SELECT COUNT(*) FROM `{base_name}`")
            restore_count = cursor.fetchone()[0]
            
            conn.commit()
            conn.close()
            
            self.log(f"✅ Wiederherstellung: {base_name} aus {selected_backup[0]} ({restore_count} Datensätze)")
            self.status_label.config(text=f"Tabelle '{base_name}' wiederhergestellt")
            
            # Tabellenliste aktualisieren
            self.tabellen_laden()
            
            messagebox.showinfo("Wiederherstellung erfolgreich", 
                               f"Tabelle '{base_name}' erfolgreich wiederhergestellt\\n\\n{restore_count} Datensätze")
            
        except Exception as e:
            messagebox.showerror("Wiederherstellungs-Fehler", f"Fehler bei der Wiederherstellung:\\n{str(e)}")
            self.log(f"❌ Wiederherstellungs-Fehler: {str(e)}")
    
    def basis_kopie_erstellen(self):
        """Erstellt eine Basis-Kopie der ausgewählten Tabelle"""
        if not self.selected_table:
            messagebox.showwarning("Keine Auswahl", "Bitte wählen Sie eine Tabelle aus.")
            return
        
        try:
            timestamp = self.get_timestamp()
            base_name = f"{self.selected_table}_base{timestamp}"
            
            # Bestätigung
            antwort = messagebox.askyesno("Basis-Kopie erstellen", 
                                         f"Basis-Kopie erstellen?\\n\\nOriginal: {self.selected_table}\\nBasis-Kopie: {base_name}")
            if not antwort:
                return
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Prüfen ob Basis-Kopie bereits existiert
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (base_name,))
            if cursor.fetchone():
                antwort2 = messagebox.askyesno("Basis-Kopie überschreiben", 
                                              f"Basis-Kopie '{base_name}' existiert bereits.\\nÜberschreiben?")
                if not antwort2:
                    conn.close()
                    return
                
                cursor.execute(f"DROP TABLE `{base_name}`")
            
            # Tabelle kopieren
            cursor.execute(f"CREATE TABLE `{base_name}` AS SELECT * FROM `{self.selected_table}`")
            
            # Datensätze zählen
            cursor.execute(f"SELECT COUNT(*) FROM `{base_name}`")
            base_count = cursor.fetchone()[0]
            
            conn.commit()
            conn.close()
            
            self.log(f"✅ Basis-Kopie erstellt: {base_name} ({base_count} Datensätze)")
            self.status_label.config(text=f"Basis-Kopie '{base_name}' erstellt")
            
            # Tabellenliste aktualisieren
            self.tabellen_laden()
            
            messagebox.showinfo("Basis-Kopie erstellt", f"Basis-Kopie erfolgreich erstellt:\\n{base_name}\\n\\n{base_count} Datensätze kopiert")
            
        except Exception as e:
            messagebox.showerror("Basis-Kopie-Fehler", f"Fehler beim Erstellen der Basis-Kopie:\\n{str(e)}")
            self.log(f"❌ Basis-Kopie-Fehler: {str(e)}")
    
    def backups_anzeigen(self):
        """Zeigt alle verfügbaren Backups für die ausgewählte Tabelle an"""
        if not self.selected_table:
            messagebox.showwarning("Keine Auswahl", "Bitte wählen Sie eine Tabelle aus.")
            return
        
        try:
            base_name = self.selected_table.split('_bak')[0].split('_base')[0]
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Alle Backups und Basis-Kopien finden
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND (name LIKE ? OR name LIKE ?) ORDER BY name", 
                          (f"{base_name}_bak%", f"{base_name}_base%"))
            backups = cursor.fetchall()
            
            conn.close()
            
            if not backups:
                messagebox.showinfo("Keine Backups", f"Keine Backups oder Basis-Kopien für '{base_name}' gefunden.")
                return
            
            # Backup-Fenster
            backup_window = tk.Toplevel(self.root)
            backup_window.title(f"Backups für '{base_name}'")
            backup_window.geometry("600x500")
            backup_window.transient(self.root)
            
            tk.Label(backup_window, text=f"Verfügbare Backups und Basis-Kopien für '{base_name}':", 
                     font=("Arial", 12, "bold"), pady=10).pack()
            
            # Treeview für Backup-Details
            tree_frame = tk.Frame(backup_window)
            tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            
            backup_tree = ttk.Treeview(tree_frame, columns=("Name", "Typ", "Datensätze"), show="headings")
            
            backup_tree.heading("Name", text="Backup/Basis Name")
            backup_tree.heading("Typ", text="Typ")
            backup_tree.heading("Datensätze", text="Datensätze")
            
            backup_tree.column("Name", width=300, anchor="w")
            backup_tree.column("Typ", width=100, anchor="center")
            backup_tree.column("Datensätze", width=100, anchor="center")
            
            backup_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=backup_tree.yview)
            backup_tree.configure(yscrollcommand=backup_scroll.set)
            
            backup_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            backup_scroll.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Backup-Details laden
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for (backup_name,) in backups:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM `{backup_name}`")
                    count = cursor.fetchone()[0]
                except:
                    count = "N/A"
                
                backup_type = "Backup" if "_bak" in backup_name else "Basis"
                backup_tree.insert("", "end", values=(backup_name, backup_type, count))
            
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Anzeigen der Backups:\\n{str(e)}")
    
    def tabelle_anzeigen(self):
        """Zeigt die ausgewählte Tabelle mit sortierbaren Spalten, Detailansicht und Gruppierung an"""
        if not self.selected_table:
            messagebox.showwarning("Keine Auswahl", "Bitte wählen Sie eine Tabelle aus.")
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Tabellen-Info abrufen
            cursor.execute(f"PRAGMA table_info(`{self.selected_table}`)")
            columns_info = cursor.fetchall()
            
            if not columns_info:
                messagebox.showinfo("Keine Spalten", f"Tabelle '{self.selected_table}' hat keine Spalten.")
                conn.close()
                return
            
            # Alle Daten abrufen
            cursor.execute(f"SELECT * FROM `{self.selected_table}`")
            all_rows = cursor.fetchall()
            conn.close()
            
            # Neues Fenster
            table_window = tk.Toplevel(self.root)
            table_window.title(f"Tabelle: {self.selected_table}")
            table_window.geometry("1400x800")
            table_window.transient(self.root)
            
            # Titel
            titel_frame = tk.Frame(table_window, bg="#007bff", pady=10)
            titel_frame.pack(fill=tk.X)
            
            tk.Label(titel_frame, text=f"📊 Tabelle: {self.selected_table} ({len(all_rows)} Zeilen)", 
                     font=("Arial", 14, "bold"), bg="#007bff", fg="white").pack()
            
            # Hauptcontainer mit Paned Window
            main_paned = ttk.PanedWindow(table_window, orient=tk.HORIZONTAL)
            main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Linke Seite - Tabelle
            left_frame = tk.LabelFrame(main_paned, text="Tabellendaten (klickbare Zeilen)", font=("Arial", 11, "bold"))
            main_paned.add(left_frame, weight=3)
            
            # Filter-Frame
            filter_frame = tk.Frame(left_frame)
            filter_frame.pack(fill=tk.X, padx=10, pady=5)
            
            # Erste Zeile - Standard Filter
            filter_row1 = tk.Frame(filter_frame)
            filter_row1.pack(fill=tk.X, pady=(0, 5))
            
            tk.Label(filter_row1, text="Standard Filter:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
            
            filter_column = ttk.Combobox(filter_row1, width=15, font=("Arial", 9))
            filter_column.pack(side=tk.LEFT, padx=5)
            
            filter_value = ttk.Combobox(filter_row1, width=20, font=("Arial", 9))
            filter_value.pack(side=tk.LEFT, padx=5)
            
            # Spalten aus Schema
            column_names = [col[1] for col in columns_info]
            filter_column['values'] = ['Alle'] + column_names
            filter_column.set('Alle')
            
            # Standard Filter-Buttons
            tk.Button(filter_row1, text="🔍 Filtern", command=lambda: apply_filter(),
                      bg="#28a745", fg="white", font=("Arial", 8, "bold")).pack(side=tk.LEFT, padx=5)
            
            tk.Button(filter_row1, text="↻ Alle", command=lambda: reset_filter(),
                      bg="#6c757d", fg="white", font=("Arial", 8, "bold")).pack(side=tk.LEFT, padx=2)
            
            # Zweite Zeile - RegEx Filter
            filter_row2 = tk.Frame(filter_frame)
            filter_row2.pack(fill=tk.X)
            
            tk.Label(filter_row2, text="RegEx Filter:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
            
            regex_column = ttk.Combobox(filter_row2, width=15, font=("Arial", 9))
            regex_column.pack(side=tk.LEFT, padx=5)
            regex_column['values'] = ['Alle'] + column_names
            regex_column.set('Alle')
            
            regex_pattern = tk.Entry(filter_row2, width=25, font=("Arial", 9))
            regex_pattern.pack(side=tk.LEFT, padx=5)
            
            # RegEx Buttons
            tk.Button(filter_row2, text="🔧 RegEx anwenden", command=lambda: apply_regex_filter(),
                      bg="#fd7e14", fg="white", font=("Arial", 8, "bold")).pack(side=tk.LEFT, padx=5)
            
            tk.Button(filter_row2, text="❓ RegEx Hilfe", command=lambda: show_regex_help(),
                      bg="#17a2b8", fg="white", font=("Arial", 8, "bold")).pack(side=tk.LEFT, padx=2)
            
            # Treeview für Tabelle
            tree_frame = tk.Frame(left_frame)
            tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            table_tree = ttk.Treeview(tree_frame, columns=column_names, show="headings")
            
            # Sortierung
            sort_column = [None]
            sort_reverse = [False]
            current_rows = [all_rows.copy()]  # Aktuell angezeigte Zeilen
            
            def sort_by_column(col):
                if sort_column[0] == col:
                    sort_reverse[0] = not sort_reverse[0]
                else:
                    sort_column[0] = col
                    sort_reverse[0] = False
                
                # Aktuelle Daten sortieren
                col_index = column_names.index(col)
                
                def sort_key(row):
                    value = row[col_index]
                    if value is None:
                        return ""
                    # Versuche numerische Sortierung, sonst String
                    try:
                        return float(value)
                    except:
                        return str(value).lower() if isinstance(value, str) else str(value)
                
                sorted_rows = sorted(current_rows[0], key=sort_key, reverse=sort_reverse[0])
                current_rows[0] = sorted_rows
                
                # Treeview neu füllen
                for item in table_tree.get_children():
                    table_tree.delete(item)
                
                for row in sorted_rows:
                    display_values = [str(val) if val is not None else "" for val in row]
                    table_tree.insert("", "end", values=display_values)
                
                # Sortier-Indikator
                for column in column_names:
                    if column == col:
                        direction = " ▼" if sort_reverse[0] else " ▲"
                        table_tree.heading(column, text=column + direction, command=lambda c=column: sort_by_column(c))
                    else:
                        table_tree.heading(column, text=column, command=lambda c=column: sort_by_column(c))
            
            def apply_filter():
                """Wendet Standard-Filter auf die Tabellendaten an"""
                filter_col = filter_column.get()
                filter_val = filter_value.get()
                
                if filter_col == 'Alle' or not filter_val:
                    # Alle Daten anzeigen
                    filtered_rows = all_rows
                else:
                    # Standard-Filterung
                    col_index = column_names.index(filter_col)
                    filtered_rows = []
                    for row in all_rows:
                        cell_value = str(row[col_index]) if row[col_index] is not None else ""
                        if filter_val.lower() in cell_value.lower():
                            filtered_rows.append(row)
                
                current_rows[0] = filtered_rows
                update_treeview(filtered_rows)
                self.log(f"🔍 Standard-Filter: {len(filtered_rows)} von {len(all_rows)} Zeilen")
            
            def apply_regex_filter():
                """Wendet RegEx-Filter auf die Tabellendaten an"""
                regex_col = regex_column.get()
                regex_pat = regex_pattern.get()
                
                if not regex_pat:
                    messagebox.showwarning("RegEx Fehler", "Bitte geben Sie ein RegEx-Pattern ein.")
                    return
                
                try:
                    import re
                    compiled_regex = re.compile(regex_pat, re.IGNORECASE)
                    
                    if regex_col == 'Alle':
                        # In allen Spalten suchen
                        filtered_rows = []
                        for row in all_rows:
                            match_found = False
                            for cell_value in row:
                                cell_str = str(cell_value) if cell_value is not None else ""
                                if compiled_regex.search(cell_str):
                                    match_found = True
                                    break
                            if match_found:
                                filtered_rows.append(row)
                    else:
                        # In spezifischer Spalte suchen
                        col_index = column_names.index(regex_col)
                        filtered_rows = []
                        for row in all_rows:
                            cell_value = str(row[col_index]) if row[col_index] is not None else ""
                            if compiled_regex.search(cell_value):
                                filtered_rows.append(row)
                    
                    current_rows[0] = filtered_rows
                    update_treeview(filtered_rows)
                    self.log(f"🔧 RegEx-Filter '{regex_pat}': {len(filtered_rows)} von {len(all_rows)} Zeilen")
                    
                except re.error as e:
                    messagebox.showerror("RegEx Fehler", f"Ungültiges RegEx-Pattern:\\n{str(e)}")
                    self.log(f"❌ RegEx-Fehler: {str(e)}")
                except Exception as e:
                    messagebox.showerror("Fehler", f"Fehler beim RegEx-Filter:\\n{str(e)}")
                    self.log(f"❌ RegEx-Filter Fehler: {str(e)}")
            
            def show_regex_help():
                """Zeigt RegEx-Hilfe an"""
                help_window = tk.Toplevel(table_window)
                help_window.title("RegEx Hilfe")
                help_window.geometry("600x500")
                help_window.transient(table_window)
                help_window.grab_set()
                
                # Titel
                tk.Label(help_window, text="🔧 Regular Expression (RegEx) Hilfe", 
                         font=("Arial", 14, "bold"), bg="#17a2b8", fg="white", pady=10).pack(fill=tk.X)
                
                # Scrollable Text
                text_frame = tk.Frame(help_window)
                text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
                
                help_text = scrolledtext.ScrolledText(text_frame, font=("Courier", 10), wrap=tk.WORD)
                help_text.pack(fill=tk.BOTH, expand=True)
                
                regex_help = '''📚 REGEX GRUNDLAGEN:
                
• .           Beliebiges Zeichen (außer Zeilenumbruch)
• \\d          Ziffer (0-9)
• \\w          Wort-Zeichen (Buchstaben, Ziffern, _)
• \\s          Leerzeichen
• ^           Zeilenanfang
• $           Zeilende
• *           0 oder mehr Wiederholungen
• +           1 oder mehr Wiederholungen
• ?           0 oder 1 Wiederholung
• {n}         Genau n Wiederholungen
• {n,m}       Zwischen n und m Wiederholungen
• [abc]       Eines der Zeichen a, b oder c
• [a-z]       Beliebiger Kleinbuchstabe
• [0-9]       Beliebige Ziffer
• [^abc]      Alles außer a, b oder c
• |           ODER-Verknüpfung
• ()          Gruppe
• \\          Escape-Zeichen

🔍 PRAKTISCHE BEISPIELE:

Zahlen finden:
• \\d+                    Eine oder mehr Ziffern
• ^\\d{4}$               Genau 4 Ziffern
• \\d{1,3}               1 bis 3 Ziffern
• \\d+\\.\\d+            Dezimalzahl (z.B. 12.34)

E-Mail Adressen:
• \\w+@\\w+\\.\\w+       Einfache E-Mail
• [\\w.-]+@[\\w.-]+\\.[a-zA-Z]{2,}  Erweiterte E-Mail

Telefonnummern:
• \\d{3}-\\d{3}-\\d{4}   Format: 123-456-7890
• \\+\\d{1,3}\\s\\d+     Internationale Nummer

Datums-Formate:
• \\d{2}\\.\\d{2}\\.\\d{4}     dd.mm.yyyy
• \\d{4}-\\d{2}-\\d{2}         yyyy-mm-dd

Namen und Text:
• ^[A-Z]\\w+             Wort beginnend mit Großbuchstabe
• \\b\\w{5}\\b           Wörter mit genau 5 Buchstaben
• (Müller|Schmidt|Weber) Namen aus Liste

IDs und Codes:
• [A-Z]{2,3}\\d+         Code: 2-3 Buchstaben + Ziffern
• REG\\d{6}              REG + 6 Ziffern
• \\w+-\\d+-\\w+         Wort-Zahl-Wort mit Bindestrichen

🎯 SPEZIELLE FILTER:

Leere/Null Werte:
• ^$                     Komplett leer
• ^\\s*$                 Nur Leerzeichen

Text-Suche:
• (?i)berlin             "berlin" (groß/klein egal)
• ^(?!.*test)            Zeilen OHNE "test"
• .*(?=.*wort1)(?=.*wort2).*  Enthält BEIDE Wörter

⚠️ WICHTIGE HINWEISE:

• RegEx ist case-insensitive (Groß-/Kleinschreibung egal)
• Spezialzeichen müssen escaped werden: \\ . + * ? [ ] ^ $ ( ) | { }
• Teste komplexe Patterns an wenigen Daten zuerst
• Bei Fehlern wird eine Fehlermeldung angezeigt

💡 TIPP: Beginnen Sie mit einfachen Patterns und erweitern Sie schrittweise!'''
                
                help_text.insert(tk.END, regex_help)
                help_text.config(state=tk.DISABLED)
                
                # Close Button
                tk.Button(help_window, text="✅ Schließen", command=help_window.destroy,
                         bg="#28a745", fg="white", font=("Arial", 11, "bold")).pack(pady=10)
            
            def update_treeview(rows_to_show):
                """Hilfsfunktion um Treeview zu aktualisieren"""
                # Treeview leeren
                for item in table_tree.get_children():
                    table_tree.delete(item)
                
                # Neue Daten einfügen
                for row in rows_to_show:
                    display_values = [str(val) if val is not None else "" for val in row]
                    table_tree.insert("", "end", values=display_values)
            
            def reset_filter():
                """Setzt alle Filter zurück"""
                filter_column.set('Alle')
                filter_value.set('')
                regex_column.set('Alle')
                regex_pattern.delete(0, tk.END)
                
                current_rows[0] = all_rows.copy()
                update_treeview(all_rows)
                self.log(f"↻ Filter zurückgesetzt: {len(all_rows)} Zeilen angezeigt")
            
            # Filter-Buttons müssen nach den Funktionsdefinitionen entfernt werden
            # da sie jetzt bereits oben definiert sind
            
            # Spalten konfigurieren
            for col in column_names:
                table_tree.heading(col, text=col, command=lambda c=col: sort_by_column(c))
                width = min(max(len(col) * 8 + 20, 80), 200)  # Dynamische Breite
                table_tree.column(col, width=width, anchor="w")
            
            # Scrollbars
            v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=table_tree.yview)
            h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=table_tree.xview)
            table_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
            
            table_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
            
            # Rechte Seite - Detailansicht
            right_frame = tk.LabelFrame(main_paned, text="Zeilen-Details", font=("Arial", 11, "bold"))
            main_paned.add(right_frame, weight=1)
            
            # Details Container mit Scrollbar
            details_canvas = tk.Canvas(right_frame)
            details_scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=details_canvas.yview)
            details_scrollable = ttk.Frame(details_canvas)
            
            details_scrollable.bind(
                "<Configure>",
                lambda e: details_canvas.configure(scrollregion=details_canvas.bbox("all"))
            )
            
            details_canvas.create_window((0, 0), window=details_scrollable, anchor="nw")
            details_canvas.configure(yscrollcommand=details_scrollbar.set)
            
            details_canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
            details_scrollbar.pack(side="right", fill="y")
            
            # Details-Widgets Container
            selected_row_data = [None]
            
            def show_row_details(selected_row):
                """Zeigt Details der ausgewählten Zeile"""
                # Alte Details löschen
                for widget in details_scrollable.winfo_children():
                    widget.destroy()
                
                if not selected_row:
                    tk.Label(details_scrollable, text="Keine Zeile ausgewählt", 
                             font=("Arial", 10), fg="gray").pack(pady=20)
                    return
                
                selected_row_data[0] = selected_row
                
                # Header
                tk.Label(details_scrollable, text="📋 Zeilen-Details", 
                         font=("Arial", 12, "bold"), fg="#007bff").pack(pady=(10, 15))
                
                # Felder anzeigen
                for i, (col_name, value) in enumerate(zip(column_names, selected_row)):
                    field_frame = tk.Frame(details_scrollable)
                    field_frame.pack(fill=tk.X, padx=10, pady=2)
                    
                    # Label (klickbar)
                    label = tk.Label(field_frame, text=f"{col_name}:", 
                                    font=("Arial", 9, "bold"), anchor="w", width=15,
                                    cursor="hand2", fg="#007bff")
                    label.pack(anchor=tk.W)
                    
                    # Value (klickbar)
                    value_str = str(value) if value is not None else ""
                    if len(value_str) > 50:
                        value_str = value_str[:47] + "..."
                    
                    value_label = tk.Label(field_frame, text=value_str, 
                                          font=("Arial", 9), anchor="w",
                                          cursor="hand2", fg="#333",
                                          bg="#f8f9fa", relief="sunken", padx=5, pady=2)
                    value_label.pack(fill=tk.X, pady=(2, 5))
                    
                    # Click-Handler für Gruppierung
                    def create_filter_handler(column, val):
                        return lambda event: group_by_field_value(column, val)
                    
                    label.bind("<Button-1>", create_filter_handler(col_name, value))
                    value_label.bind("<Button-1>", create_filter_handler(col_name, value))
                    
                    # Tooltip-Effekt
                    def on_enter(event, widget=value_label):
                        widget.config(bg="#e9ecef")
                    
                    def on_leave(event, widget=value_label):
                        widget.config(bg="#f8f9fa")
                    
                    value_label.bind("<Enter>", on_enter)
                    value_label.bind("<Leave>", on_leave)
                
                # Info-Text
                if selected_row_data[0]:
                    button_frame = tk.Frame(details_scrollable)
                    button_frame.pack(fill=tk.X, padx=10, pady=15)
                    
                    tk.Label(button_frame, text="💡 Tipp: Klicken Sie auf ein Feld um nach diesem Wert zu gruppieren", 
                             font=("Arial", 8), fg="gray", wraplength=200).pack()
            
            def group_by_field_value(field_name, field_value):
                """Gruppiert Tabelle nach dem angeklickten Feldwert"""
                try:
                    if field_name not in column_names:
                        return
                    
                    col_index = column_names.index(field_name)
                    
                    # Nach Feldwert filtern
                    filtered_rows = []
                    search_value = str(field_value) if field_value is not None else ""
                    
                    for row in all_rows:
                        cell_value = str(row[col_index]) if row[col_index] is not None else ""
                        if cell_value == search_value:
                            filtered_rows.append(row)
                    
                    # Current rows referenz aktualisieren
                    current_rows[0] = filtered_rows
                    
                    # Filter-Combobox aktualisieren
                    filter_column.set(field_name)
                    filter_value.set(search_value)
                    
                    update_treeview(filtered_rows)
                    
                    # Log-Nachricht
                    self.log(f"🔍 Gruppiert nach {field_name} = '{search_value}' ({len(filtered_rows)} Zeilen)")
                    
                except Exception as e:
                    self.log(f"❌ Fehler bei Gruppierung: {str(e)}")
            
            # Event für Zeilenauswahl
            def on_row_select(event):
                selection = table_tree.selection()
                if selection:
                    item = table_tree.item(selection[0])
                    values = item['values']
                    # Zurück zu ursprünglichen Datentypen konvertieren
                    row_data = []
                    for i, val in enumerate(values):
                        if val == "":
                            row_data.append(None)
                        else:
                            row_data.append(val)
                    show_row_details(row_data)
                else:
                    show_row_details(None)
            
            table_tree.bind('<<TreeviewSelect>>', on_row_select)
            
            # Daten initial einfügen
            for row in all_rows:
                display_values = [str(val) if val is not None else "" for val in row]
                table_tree.insert("", "end", values=display_values)
            
            # Initial Details
            show_row_details(None)
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Anzeigen der Tabelle:\\n{str(e)}")
            self.log(f"❌ Fehler beim Anzeigen der Tabelle: {str(e)}")
    
    def an_base_anhaengen(self):
        """Hängt die ausgewählte Tabelle an die entsprechende Base-Tabelle an"""
        if not self.selected_table:
            messagebox.showwarning("Keine Auswahl", "Bitte wählen Sie eine Tabelle aus.")
            return
        
        try:
            # Base-Tabellenname ermitteln
            base_table_name = self.selected_table.split('_bak')[0].split('_base')[0]
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Prüfen ob Base-Tabelle existiert
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE ? ORDER BY name DESC", 
                          (f"{base_table_name}_base%",))
            base_tables = cursor.fetchall()
            
            if not base_tables:
                messagebox.showinfo("Keine Base-Tabelle", 
                                   f"Keine Base-Tabelle für '{base_table_name}' gefunden.\\n\\n"
                                   f"Erstellen Sie zuerst eine Base-Tabelle mit dem Button 'Basis-Kopie erstellen'.")
                conn.close()
                return
            
            # Neueste Base-Tabelle wählen (falls mehrere vorhanden)
            target_base_table = base_tables[0][0]
            
            # Tabellenstrukturen vergleichen
            cursor.execute(f"PRAGMA table_info(`{self.selected_table}`)")
            source_columns = [col[1] for col in cursor.fetchall()]
            
            cursor.execute(f"PRAGMA table_info(`{target_base_table}`)")
            target_columns = [col[1] for col in cursor.fetchall()]
            
            if source_columns != target_columns:
                messagebox.showerror("Struktur-Fehler", 
                                    f"Tabellenstrukturen sind unterschiedlich!\\n\\n"
                                    f"Quelle ({self.selected_table}): {len(source_columns)} Spalten\\n"
                                    f"Ziel ({target_base_table}): {len(target_columns)} Spalten\\n\\n"
                                    f"Die Strukturen müssen identisch sein.")
                conn.close()
                return
            
            # Anzahl Datensätze ermitteln
            cursor.execute(f"SELECT COUNT(*) FROM `{self.selected_table}`")
            source_count = cursor.fetchone()[0]
            
            cursor.execute(f"SELECT COUNT(*) FROM `{target_base_table}`")
            target_count_before = cursor.fetchone()[0]
            
            # Bestätigung
            antwort = messagebox.askyesno("An Base-Tabelle anhängen", 
                                         f"Möchten Sie alle Daten aus '{self.selected_table}' \\n"
                                         f"an '{target_base_table}' anhängen?\\n\\n"
                                         f"Quelle: {source_count} Datensätze\\n"
                                         f"Ziel (vorher): {target_count_before} Datensätze\\n\\n"
                                         f"Die Daten werden am Ende der Base-Tabelle angefügt.")
            
            if not antwort:
                conn.close()
                return
            
            # Daten anhängen
            column_list = ', '.join([f'`{col}`' for col in source_columns])
            cursor.execute(f"INSERT INTO `{target_base_table}` ({column_list}) SELECT {column_list} FROM `{self.selected_table}`")
            
            # Erfolg prüfen
            cursor.execute(f"SELECT COUNT(*) FROM `{target_base_table}`")
            target_count_after = cursor.fetchone()[0]
            
            added_records = target_count_after - target_count_before
            
            conn.commit()
            conn.close()
            
            self.log(f"✅ Daten angehängt: {added_records} Datensätze von '{self.selected_table}' zu '{target_base_table}'")
            self.status_label.config(text=f"{added_records} Datensätze an '{target_base_table}' angehängt")
            
            # Tabellenliste aktualisieren
            self.tabellen_laden()
            
            messagebox.showinfo("Anhängen erfolgreich", 
                               f"Erfolgreich angehängt!\\n\\n"
                               f"Von: {self.selected_table}\\n"
                               f"Nach: {target_base_table}\\n\\n"
                               f"{added_records} Datensätze hinzugefügt\\n"
                               f"Gesamt in Base-Tabelle: {target_count_after}")
            
        except Exception as e:
            messagebox.showerror("Anhänge-Fehler", f"Fehler beim Anhängen an Base-Tabelle:\\n{str(e)}")
            self.log(f"❌ Anhänge-Fehler: {str(e)}")
    
    def tabelle_loeschen(self):
        """Löscht die ausgewählte Tabelle"""
        if not self.selected_table:
            messagebox.showwarning("Keine Auswahl", "Bitte wählen Sie eine Tabelle aus.")
            return
        
        # Mehrfache Bestätigung für Sicherheit
        antwort1 = messagebox.askyesno("Tabelle löschen - Bestätigung 1", 
                                      f"Möchten Sie die Tabelle '{self.selected_table}' wirklich löschen?\\n\\n"
                                      f"ACHTUNG: Dieser Vorgang kann NICHT rückgängig gemacht werden!")
        
        if not antwort1:
            return
        
        antwort2 = messagebox.askyesno("Tabelle löschen - Bestätigung 2", 
                                      f"LETZTE WARNUNG!\\n\\nTabelle '{self.selected_table}' wird unwiderruflich gelöscht!\\n\\n"
                                      f"Sind Sie absolut sicher?",
                                      icon='warning')
        
        if not antwort2:
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Anzahl Datensätze vor Löschung ermitteln
            cursor.execute(f"SELECT COUNT(*) FROM `{self.selected_table}`")
            record_count = cursor.fetchone()[0]
            
            # Tabelle löschen
            cursor.execute(f"DROP TABLE `{self.selected_table}`")
            
            conn.commit()
            conn.close()
            
            self.log(f"🗑️ Tabelle gelöscht: {self.selected_table} ({record_count} Datensätze)")
            self.status_label.config(text=f"Tabelle '{self.selected_table}' gelöscht")
            
            # Auswahl zurücksetzen
            self.selected_table = None
            self.lbl_selected.config(text="Keine Tabelle ausgewählt")
            
            # Buttons deaktivieren
            self.btn_create_backup.config(state=tk.DISABLED)
            self.btn_restore_backup.config(state=tk.DISABLED)
            self.btn_create_base.config(state=tk.DISABLED)
            self.btn_show_backups.config(state=tk.DISABLED)
            self.btn_show_table.config(state=tk.DISABLED)
            self.btn_append_to_base.config(state=tk.DISABLED)
            self.btn_delete_table.config(state=tk.DISABLED)
            
            # Tabellenliste aktualisieren
            self.tabellen_laden()
            
            messagebox.showinfo("Tabelle gelöscht", f"Tabelle '{self.selected_table}' wurde gelöscht.\\n\\n{record_count} Datensätze entfernt.")
            
        except Exception as e:
            messagebox.showerror("Lösch-Fehler", f"Fehler beim Löschen der Tabelle:\\n{str(e)}")
            self.log(f"❌ Lösch-Fehler: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = DatabaseBackupManager(root)
    root.mainloop()