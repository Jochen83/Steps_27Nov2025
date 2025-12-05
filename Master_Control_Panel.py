import tkinter as tk
from tkinter import messagebox, ttk
import subprocess
import threading
import os
import sys
from datetime import datetime

# Master Control Panel für alle Regatta-Tools
# Erstellt am 01.12.2025

class MasterControlPanel:
    def __init__(self, root):
        self.root = root
        self.root.title("Regatta-Tools Master Control Panel")
        self.root.geometry("1000x700")
        
        # Variablen
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.script_dir = script_dir
        self.laufende_prozesse = {}
        
        # Anwendungen definieren
        self.anwendungen = {
            1: {
                'name': 'Step1 Unified Extractor',
                'datei': 'Step1_unified_extractor.py',
                'beschreibung': 'OCR/PDF Text-Extraktion und Export',
                'icon': '📄',
                'farbe': '#6f42c1'
            },
            2: {
                'name': 'Tabellen Import',
                'datei': 'Tabell_Import.py',
                'beschreibung': 'CSV/TXT Import mit Headers in Datenbank',
                'icon': '📊',
                'farbe': '#17a2b8'
            },
            3: {
                'name': 'Regex Treffer',
                'datei': 'Regex_Treffer.py',
                'beschreibung': 'Pattern-Suche und Hit-Extraktion',
                'icon': '🔍',
                'farbe': '#28a745'
            },
            4: {
                'name': 'Tabellen Abgleich',
                'datei': 'Tabellen_Abgleich.py',
                'beschreibung': 'Regelbasierter Tabellen-Abgleich',
                'icon': '🔄',
                'farbe': '#fd7e14'
            },
            5: {
                'name': 'Verein Treffer Match',
                'datei': 'Verein_Treffer_Match.py',
                'beschreibung': 'Club/Verein Name Matching',
                'icon': '🏆',
                'farbe': '#dc3545'
            },
            6: {
                'name': 'Regatta Verwaltung',
                'datei': 'Regatta_Verwaltung.py',
                'beschreibung': 'Regatta-Stammdaten verwalten und Import steuern',
                'icon': '🏁',
                'farbe': '#e83e8c'
            },
            7: {
                'name': 'Database Backup Manager',
                'datei': 'Database_Backup_Manager.py',
                'beschreibung': 'Datenbank Backup, Wiederherstellung und Basis-Kopien',
                'icon': '🗄️',
                'farbe': '#6c757d'
            },
            8: {
                'name': 'Inhalts-Gruppierung',
                'datei': 'Gruppierung.py',
                'beschreibung': 'Feldinhalt-Analyse und Typisierung',
                'icon': '📈',
                'farbe': '#20c997'
            }
        }
        
        # GUI erstellen
        self.gui_erstellen()
        
        # Timer für Status-Updates
        self.status_update_timer()
    
    def gui_erstellen(self):
        """Erstellt die GUI-Elemente"""
        
        # Titel
        titel_frame = tk.Frame(self.root, bg="#2c3e50", pady=20)
        titel_frame.pack(fill=tk.X)
        
        tk.Label(titel_frame, text="🏁 Regatta-Tools Master Control Panel", 
                 font=("Arial", 18, "bold"), fg="white", bg="#2c3e50").pack()
        tk.Label(titel_frame, text="Zentrale Steuerung für alle Regatta-Datenverarbeitungs-Tools", 
                 font=("Arial", 11), fg="#bdc3c7", bg="#2c3e50").pack()
        
        # Hauptcontainer
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Control Buttons Frame
        control_frame = tk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Alle starten Button
        self.btn_alle_starten = tk.Button(control_frame, text="🚀 Alle Tools starten", 
                                          command=self.alle_starten,
                                          bg="#28a745", fg="white", height=2, width=20,
                                          font=("Arial", 12, "bold"))
        self.btn_alle_starten.pack(side=tk.LEFT, padx=(0, 10))
        
        # Alle beenden Button
        self.btn_alle_beenden = tk.Button(control_frame, text="⏹️ Alle Tools beenden", 
                                          command=self.alle_beenden,
                                          bg="#dc3545", fg="white", height=2, width=20,
                                          font=("Arial", 12, "bold"))
        self.btn_alle_beenden.pack(side=tk.LEFT, padx=(0, 10))
        
        # Status anzeigen Button
        self.btn_status = tk.Button(control_frame, text="📊 Status anzeigen", 
                                    command=self.status_anzeigen,
                                    bg="#17a2b8", fg="white", height=2, width=20,
                                    font=("Arial", 12, "bold"))
        self.btn_status.pack(side=tk.LEFT)
        
        # Anwendungen Frame
        apps_frame = tk.LabelFrame(main_frame, text="Verfügbare Anwendungen", 
                                   font=("Arial", 14, "bold"), pady=10)
        apps_frame.pack(fill=tk.BOTH, expand=True)
        
        # Grid für Anwendung-Karten
        self.app_frames = {}
        self.app_buttons = {}
        self.status_labels = {}
        
        # 3x3 Grid angepasst für 8 Anwendungen
        for i, (app_id, app_info) in enumerate(self.anwendungen.items()):
            row = i // 3
            col = i % 3
            
            # App-Karte Frame
            app_frame = tk.Frame(apps_frame, relief=tk.RAISED, bd=2)
            app_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            
            # Grid-Gewichtung
            apps_frame.grid_columnconfigure(col, weight=1)
            apps_frame.grid_rowconfigure(row, weight=1)
            
            # App-Info
            info_frame = tk.Frame(app_frame, bg=app_info['farbe'], pady=10)
            info_frame.pack(fill=tk.X)
            
            tk.Label(info_frame, text=f"{app_info['icon']} {app_info['name']}", 
                     font=("Arial", 12, "bold"), fg="white", bg=app_info['farbe']).pack()
            tk.Label(info_frame, text=app_info['beschreibung'], 
                     font=("Arial", 9), fg="white", bg=app_info['farbe'], wraplength=200).pack()
            
            # Buttons Frame
            btn_frame = tk.Frame(app_frame, pady=5)
            btn_frame.pack(fill=tk.X)
            
            # Start Button
            start_btn = tk.Button(btn_frame, text="▶️ Starten", 
                                  command=lambda aid=app_id: self.app_starten(aid),
                                  bg="#28a745", fg="white", width=10, height=1,
                                  font=("Arial", 9, "bold"))
            start_btn.pack(side=tk.LEFT, padx=2)
            
            # Stop Button
            stop_btn = tk.Button(btn_frame, text="⏹️ Beenden", 
                                 command=lambda aid=app_id: self.app_beenden(aid),
                                 bg="#dc3545", fg="white", width=10, height=1,
                                 font=("Arial", 9, "bold"))
            stop_btn.pack(side=tk.LEFT, padx=2)
            
            # Status Label
            status_label = tk.Label(app_frame, text="● Gestoppt", 
                                    font=("Arial", 9, "bold"), fg="#dc3545")
            status_label.pack(pady=5)
            
            # Speichern für späteren Zugriff
            self.app_frames[app_id] = app_frame
            self.app_buttons[app_id] = {'start': start_btn, 'stop': stop_btn}
            self.status_labels[app_id] = status_label
        
        # Log Frame
        log_frame = tk.LabelFrame(main_frame, text="Aktivitäts-Log", 
                                  font=("Arial", 12, "bold"))
        log_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Log Text mit Scrollbar
        log_container = tk.Frame(log_frame)
        log_container.pack(fill=tk.X, padx=10, pady=5)
        
        self.log_text = tk.Text(log_container, height=8, font=("Courier", 9), bg="#f8f9fa")
        log_scrollbar = tk.Scrollbar(log_container, command=self.log_text.yview)
        self.log_text.config(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.X, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Log leeren Button
        tk.Button(log_frame, text="🗑️ Log leeren", command=self.log_leeren,
                  bg="#6c757d", fg="white", font=("Arial", 9)).pack(pady=5)
        
        # Statusleiste
        self.status_label = tk.Label(self.root, text="Bereit - Alle Tools gestoppt", 
                                     bg="#e0e0e0", anchor=tk.W, font=("Arial", 9))
        self.status_label.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Initial log
        self.log_hinzufuegen("Master Control Panel gestartet")
    
    def log_hinzufuegen(self, nachricht):
        """Fügt eine Nachricht zum Log hinzu"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {nachricht}\n")
        self.log_text.see(tk.END)
    
    def log_leeren(self):
        """Leert das Log"""
        self.log_text.delete(1.0, tk.END)
        self.log_hinzufuegen("Log geleert")
    
    def app_starten(self, app_id):
        """Startet eine einzelne Anwendung"""
        app_info = self.anwendungen[app_id]
        datei_pfad = os.path.join(self.script_dir, app_info['datei'])
        
        # Prüfen ob Datei existiert
        if not os.path.exists(datei_pfad):
            messagebox.showerror("Fehler", f"Datei nicht gefunden:\n{datei_pfad}")
            self.log_hinzufuegen(f"FEHLER: {app_info['name']} - Datei nicht gefunden")
            return
        
        # Prüfen ob bereits läuft
        if app_id in self.laufende_prozesse and self.laufende_prozesse[app_id].poll() is None:
            messagebox.showwarning("Bereits aktiv", f"{app_info['name']} läuft bereits!")
            return
        
        try:
            # Prozess starten
            prozess = subprocess.Popen([sys.executable, datei_pfad], 
                                       cwd=self.script_dir,
                                       creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0)
            
            self.laufende_prozesse[app_id] = prozess
            self.status_labels[app_id].config(text="● Läuft", fg="#28a745")
            
            self.log_hinzufuegen(f"Gestartet: {app_info['name']} (PID: {prozess.pid})")
            self.status_update()
            
        except Exception as e:
            messagebox.showerror("Start-Fehler", f"Fehler beim Starten von {app_info['name']}:\n{str(e)}")
            self.log_hinzufuegen(f"FEHLER beim Starten: {app_info['name']} - {str(e)}")
    
    def app_beenden(self, app_id):
        """Beendet eine einzelne Anwendung"""
        app_info = self.anwendungen[app_id]
        
        if app_id not in self.laufende_prozesse:
            self.log_hinzufuegen(f"{app_info['name']} läuft nicht")
            return
        
        prozess = self.laufende_prozesse[app_id]
        
        if prozess.poll() is not None:
            # Prozess bereits beendet
            del self.laufende_prozesse[app_id]
            self.status_labels[app_id].config(text="● Gestoppt", fg="#dc3545")
            self.log_hinzufuegen(f"{app_info['name']} bereits beendet")
            self.status_update()
            return
        
        try:
            # Prozess beenden
            prozess.terminate()
            
            # Warten auf Beendigung (max 5 Sekunden)
            def warten_auf_beendigung():
                try:
                    prozess.wait(timeout=5)
                    if app_id in self.laufende_prozesse:
                        del self.laufende_prozesse[app_id]
                    self.status_labels[app_id].config(text="● Gestoppt", fg="#dc3545")
                    self.log_hinzufuegen(f"Beendet: {app_info['name']}")
                    self.status_update()
                except subprocess.TimeoutExpired:
                    # Forcierte Beendigung
                    prozess.kill()
                    if app_id in self.laufende_prozesse:
                        del self.laufende_prozesse[app_id]
                    self.status_labels[app_id].config(text="● Forciert beendet", fg="#ffc107")
                    self.log_hinzufuegen(f"Forciert beendet: {app_info['name']}")
                    self.status_update()
            
            # In separatem Thread ausführen
            threading.Thread(target=warten_auf_beendigung, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Beenden-Fehler", f"Fehler beim Beenden von {app_info['name']}:\n{str(e)}")
            self.log_hinzufuegen(f"FEHLER beim Beenden: {app_info['name']} - {str(e)}")
    
    def alle_starten(self):
        """Startet alle Anwendungen"""
        antwort = messagebox.askyesno("Alle starten?", 
                                     "Möchten Sie alle 6 Tools gleichzeitig starten?\n\nDies öffnet 6 separate Fenster.")
        if not antwort:
            return
        
        self.log_hinzufuegen("Starte alle Tools...")
        
        for app_id in self.anwendungen.keys():
            self.app_starten(app_id)
        
        self.log_hinzufuegen("Alle verfügbaren Tools wurden gestartet")
    
    def alle_beenden(self):
        """Beendet alle Anwendungen"""
        if not self.laufende_prozesse:
            messagebox.showinfo("Keine Prozesse", "Es laufen derzeit keine Tools.")
            return
        
        antwort = messagebox.askyesno("Alle beenden?", 
                                     f"Möchten Sie alle {len(self.laufende_prozesse)} laufenden Tools beenden?")
        if not antwort:
            return
        
        self.log_hinzufuegen("Beende alle Tools...")
        
        for app_id in list(self.laufende_prozesse.keys()):
            self.app_beenden(app_id)
        
        self.log_hinzufuegen("Alle Tools werden beendet...")
    
    def status_anzeigen(self):
        """Zeigt den aktuellen Status aller Tools"""
        laufend = 0
        gestoppt = 0
        
        status_text = "=== TOOL STATUS ===\n\n"
        
        for app_id, app_info in self.anwendungen.items():
            if app_id in self.laufende_prozesse and self.laufende_prozesse[app_id].poll() is None:
                status = "🟢 LÄUFT"
                pid = self.laufende_prozesse[app_id].pid
                status_text += f"{app_info['icon']} {app_info['name']}: {status} (PID: {pid})\n"
                laufend += 1
            else:
                status = "🔴 GESTOPPT"
                status_text += f"{app_info['icon']} {app_info['name']}: {status}\n"
                gestoppt += 1
        
        status_text += f"\n=== ZUSAMMENFASSUNG ===\n"
        status_text += f"Laufende Tools: {laufend}\n"
        status_text += f"Gestoppte Tools: {gestoppt}\n"
        status_text += f"Gesamt: {len(self.anwendungen)}"
        
        messagebox.showinfo("Tool Status", status_text)
    
    def status_update(self):
        """Aktualisiert die Statusleiste"""
        laufend = sum(1 for app_id in self.laufende_prozesse 
                      if self.laufende_prozesse[app_id].poll() is None)
        
        if laufend == 0:
            self.status_label.config(text="Bereit - Alle Tools gestoppt")
        elif laufend == len(self.anwendungen):
            self.status_label.config(text=f"Alle {len(self.anwendungen)} Tools aktiv")
        else:
            self.status_label.config(text=f"{laufend} von {len(self.anwendungen)} Tools aktiv")
    
    def status_update_timer(self):
        """Timer für regelmäßige Status-Updates"""
        # Überprüfe beendete Prozesse
        zu_entfernen = []
        for app_id, prozess in self.laufende_prozesse.items():
            if prozess.poll() is not None:
                zu_entfernen.append(app_id)
        
        for app_id in zu_entfernen:
            app_info = self.anwendungen[app_id]
            del self.laufende_prozesse[app_id]
            self.status_labels[app_id].config(text="● Gestoppt", fg="#dc3545")
            self.log_hinzufuegen(f"Automatisch erkannt: {app_info['name']} wurde beendet")
        
        if zu_entfernen:
            self.status_update()
        
        # Timer wiederholen
        self.root.after(2000, self.status_update_timer)
    
    def on_closing(self):
        """Wird beim Schließen des Fensters aufgerufen"""
        if self.laufende_prozesse:
            antwort = messagebox.askyesno("Beenden?", 
                                         f"Es laufen noch {len(self.laufende_prozesse)} Tools.\n\nTrotzdem beenden?\n(Tools laufen weiter)")
            if not antwort:
                return
        
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = MasterControlPanel(root)
    
    # Schließen-Event behandeln
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    root.mainloop()