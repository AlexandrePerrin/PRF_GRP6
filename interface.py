import tkinter as tk
from tkinter import ttk
from threading import Thread
import enregistreur

class VoiceApp:
    def __init__(self, master):
        self.master = master
        master.title("Reconnaissance vocale")
        master.geometry("500x350")

        self.recorder = None
        self.recording_thread = None

        self.create_widgets()

    def create_widgets(self):
        self.label_info = ttk.Label(self.master, text="Cliquez pour contrôler l'enregistrement :")
        self.label_info.pack(pady=10)

        self.start_button = ttk.Button(self.master, text="🎤 Démarrer", command=self.start_recording)
        self.start_button.pack(pady=5)

        self.stop_button = ttk.Button(self.master, text="🛑 Arrêter", command=self.stop_recording, state=tk.DISABLED)
        self.stop_button.pack(pady=5)

        self.output_label = ttk.Label(self.master, text="Transcription :", font=('Helvetica', 10, 'bold'))
        self.output_label.pack(pady=10)

        self.text_output = tk.Text(self.master, height=7, width=60, wrap=tk.WORD)
        self.text_output.pack(pady=5)

        self.quit_button = ttk.Button(self.master, text="Quitter", command=self.master.quit)
        self.quit_button.pack(pady=10)

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

def main():
    root = tk.Tk()
    app = VoiceApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
