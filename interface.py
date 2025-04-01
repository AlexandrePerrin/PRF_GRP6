import tkinter as tk
from tkinter import ttk
from threading import Thread
import enregistreur

class VoiceApp:
    def __init__(self, master, frame):
        self.master = master
        self.frame = frame
        self.recorder = None
        self.recording_thread = None
        self.build_ui()

    def build_ui(self):
        for widget in self.frame.winfo_children():
            widget.destroy()

        ttk.Label(self.frame, text="Commande Vocale", font=('Helvetica', 14, 'bold')).pack(pady=10)

        ttk.Label(self.frame, text="Cliquez pour contrôler l'enregistrement :").pack(pady=10)

        self.start_button = ttk.Button(self.frame, text="🎤 Démarrer", command=self.start_recording)
        self.start_button.pack(pady=5)

        self.stop_button = ttk.Button(self.frame, text="🛑 Arrêter", command=self.stop_recording, state=tk.DISABLED)
        self.stop_button.pack(pady=5)

        ttk.Label(self.frame, text="Transcription :", font=('Helvetica', 10, 'bold')).pack(pady=10)

        self.text_output = tk.Text(self.frame, height=7, width=60, wrap=tk.WORD)
        self.text_output.pack(pady=5)

        ttk.Button(self.frame, text="⬅️ Retour", command=self.go_back).pack(pady=10)

    def start_recording(self):
        self.recorder = enregistreur.AudioRecorder()
        self.recording_thread = Thread(target=self.recorder.start)
        self.recording_thread.start()
        self.display_message("🎙️ Enregistrement en cours... Cliquez sur 'Arrêter' quand vous avez terminé.")
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

    def stop_recording(self):
        self.recorder.stop()
        self.recording_thread.join()
        phrase = enregistreur.transcribe_audio()
        if phrase:
            self.display_message("✅ Transcription terminée :\n" + phrase)
            filepath = enregistreur.save_to_file(phrase)
            print(f"💾 Transcription enregistrée dans : {filepath}")
        else:
            self.display_message("❌ Aucun texte reconnu.")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def display_message(self, text):
        self.text_output.delete(1.0, tk.END)
        self.text_output.insert(tk.END, text)

    def go_back(self):
        show_main_menu(self.master, self.frame)

class ManualControlApp:
    def __init__(self, master, frame):
        self.master = master
        self.frame = frame
        self.build_ui()

    def build_ui(self):
        for widget in self.frame.winfo_children():
            widget.destroy()

        ttk.Label(self.frame, text="Contrôle Manuel", font=('Helvetica', 14, 'bold')).pack(pady=10)

        btn_frame = ttk.Frame(self.frame)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="⬆️ Avancer", command=lambda: self.action("Avancer")).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(btn_frame, text="⬅️ Gauche", command=lambda: self.action("Gauche")).grid(row=1, column=0, padx=5, pady=5)
        ttk.Button(btn_frame, text="➡️ Droite", command=lambda: self.action("Droite")).grid(row=1, column=2, padx=5, pady=5)
        ttk.Button(btn_frame, text="⬇️ Reculer", command=lambda: self.action("Reculer")).grid(row=2, column=1, padx=5, pady=5)

        ttk.Button(self.frame, text="⬅️ Retour", command=self.go_back).pack(pady=10)

        self.output = tk.Text(self.frame, height=3, width=40)
        self.output.pack()

    def action(self, direction):
        self.output.delete(1.0, tk.END)
        self.output.insert(tk.END, f"🔧 Action : {direction}")

    def go_back(self):
        show_main_menu(self.master, self.frame)

def show_main_menu(master, frame):
    for widget in frame.winfo_children():
        widget.destroy()

    ttk.Label(frame, text="Choisissez un mode :", font=('Helvetica', 14, 'bold')).pack(pady=20)

    ttk.Button(frame, text="🎤 Commande Vocale", command=lambda: VoiceApp(master, frame)).pack(pady=10)
    ttk.Button(frame, text="🕹️ Contrôle Manuel", command=lambda: ManualControlApp(master, frame)).pack(pady=10)
    ttk.Button(frame, text="Quitter", command=master.quit).pack(pady=10)

def main():
    root = tk.Tk()
    root.title("Interface de Commande")
    root.geometry("500x400")

    main_frame = ttk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True)

    show_main_menu(root, main_frame)

    root.mainloop()

if __name__ == "__main__":
    main()
