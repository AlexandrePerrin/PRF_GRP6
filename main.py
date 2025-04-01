import asyncio
import threading
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput

# Paramètres BLE
HM10_ADDRESS = "D8:A9:8B:C4:0F:3D"
UART_CHAR_UUID = "0000ffe1-0000-1000-8000-00805f9b34fb"


# ScreenManager avec connexion BLE partagée
class MainScreenManager(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ble_client = None
        self.ble_loop = asyncio.new_event_loop()
        t = threading.Thread(target=self.run_ble_loop, daemon=True)
        t.start()
        asyncio.run_coroutine_threadsafe(self.ble_connect(), self.ble_loop)
        self.add_widget(HomeScreen(name='home'))
        self.add_widget(VoiceCommandScreen(name='voice'))
        self.add_widget(ManualControlScreen(name='manual'))

    def run_ble_loop(self):
        asyncio.set_event_loop(self.ble_loop)
        self.ble_loop.run_forever()

    async def ble_connect(self):
        from bleak import BleakClient
        try:
            self.ble_client = BleakClient(HM10_ADDRESS)
            await self.ble_client.connect()
            print("Connecté à l'Arduino via BLE")
        except Exception as e:
            print("Erreur de connexion BLE :", e)


# Écran Home (menu principal)
class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        layout.add_widget(Label(text="Choisissez un mode :", font_size='24sp', bold=True))
        btn_voice = Button(text="Commande Vocale")
        btn_voice.bind(on_press=lambda instance: setattr(self.manager, 'current', 'voice'))
        layout.add_widget(btn_voice)
        btn_manual = Button(text="Contrôle Manuel")
        btn_manual.bind(on_press=lambda instance: setattr(self.manager, 'current', 'manual'))
        layout.add_widget(btn_manual)
        btn_quit = Button(text="Quitter")
        btn_quit.bind(on_press=lambda instance: App.get_running_app().stop())
        layout.add_widget(btn_quit)
        self.add_widget(layout)


# Écran de Commande Vocale
class VoiceCommandScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.recorder = None
        self.recording_thread = None
        self.build_ui()

    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        layout.add_widget(Label(text="Commande Vocale", font_size='24sp', bold=True, size_hint=(1, 0.1)))
        layout.add_widget(Label(text="Cliquez pour démarrer l'enregistrement :", size_hint=(1, 0.1)))
        btn_layout = BoxLayout(size_hint=(1, 0.2), spacing=10)
        self.start_button = Button(text="Démarrer")
        self.start_button.bind(on_press=self.start_recording)
        btn_layout.add_widget(self.start_button)
        self.stop_button = Button(text="Arrêter", disabled=True)
        self.stop_button.bind(on_press=self.stop_recording)
        btn_layout.add_widget(self.stop_button)
        layout.add_widget(btn_layout)
        layout.add_widget(Label(text="Transcription :", font_size='18sp', bold=True, size_hint=(1, 0.1)))
        self.text_output = TextInput(readonly=True, size_hint=(1, 0.4))
        layout.add_widget(self.text_output)
        back_button = Button(text="Retour", size_hint=(1, 0.1))
        back_button.bind(on_press=lambda instance: setattr(self.manager, 'current', 'home'))
        layout.add_widget(back_button)
        self.add_widget(layout)

    def start_recording(self, instance):
        import enregistreur
        self.recorder = enregistreur.AudioRecorder()
        self.recording_thread = threading.Thread(target=self.recorder.start)
        self.recording_thread.start()
        self.text_output.text = "Enregistrement en cours... Cliquez sur 'Arrêter' pour terminer."
        self.start_button.disabled = True
        self.stop_button.disabled = False

    def stop_recording(self, instance):
        import enregistreur
        if self.recorder:
            self.recorder.stop()
            self.recording_thread.join()
            phrase = enregistreur.transcribe_audio()
            if phrase:
                self.text_output.text = "Transcription terminée :\n" + phrase
                filepath = enregistreur.save_to_file(phrase)
                print(f"Transcription enregistrée dans : {filepath}")
                self.send_command(phrase)
            else:
                self.text_output.text = "Aucun texte reconnu."
            self.start_button.disabled = False
            self.stop_button.disabled = True

    def send_command(self, command):
        ble_client = self.manager.ble_client
        ble_loop = self.manager.ble_loop
        if ble_client is None or not ble_client.is_connected:
            self.text_output.text += "\nBLE client non connecté!"
            return
        self.text_output.text += "\nCommande envoyée : " + command
        data = (command + "\n").encode("utf-8")
        future = asyncio.run_coroutine_threadsafe(
            ble_client.write_gatt_char(UART_CHAR_UUID, data),
            ble_loop
        )
        try:
            future.result()
        except Exception as e:
            self.text_output.text += "\nErreur lors de l'envoi de la commande : " + str(e)


# Écran de Contrôle Manuel avec boutons de commande
class ManualControlScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        title = Label(text="Contrôle Manuel", font_size='24sp', bold=True, size_hint=(1, 0.1))
        main_layout.add_widget(title)

        # Grille pour les boutons de contrôle
        grid = GridLayout(cols=3, rows=3, size_hint=(1, 0.5), padding=10, spacing=10)
        grid.add_widget(Label(text=""))
        btn_avance = Button(text="AVANCE")
        btn_avance.bind(on_press=lambda instance: self.send_command("AVANCE"))
        grid.add_widget(btn_avance)
        grid.add_widget(Label(text=""))

        btn_gauche = Button(text="GAUCHE")
        btn_gauche.bind(on_press=lambda instance: self.send_command("GAUCHE"))
        grid.add_widget(btn_gauche)
        btn_stop = Button(text="STOP")
        btn_stop.bind(on_press=lambda instance: self.send_command("STOP"))
        grid.add_widget(btn_stop)
        btn_droite = Button(text="DROITE")
        btn_droite.bind(on_press=lambda instance: self.send_command("DROITE"))
        grid.add_widget(btn_droite)

        grid.add_widget(Label(text=""))
        btn_recule = Button(text="RECULE")
        btn_recule.bind(on_press=lambda instance: self.send_command("RECULE"))
        grid.add_widget(btn_recule)
        grid.add_widget(Label(text=""))

        main_layout.add_widget(grid)

        # Zone de feedback
        self.log_output = TextInput(readonly=True, size_hint=(1, 0.2))
        main_layout.add_widget(self.log_output)

        # Bouton de retour
        back_button = Button(text="Retour", size_hint=(1, 0.1))
        back_button.bind(on_press=lambda instance: setattr(self.manager, 'current', 'home'))
        main_layout.add_widget(back_button)

        self.add_widget(main_layout)

    def send_command(self, command):
        ble_client = self.manager.ble_client
        ble_loop = self.manager.ble_loop
        if ble_client is None or not ble_client.is_connected:
            self.log_output.text += "\nBLE client non connecté!"
            return
        self.log_output.text += "\nCommande envoyée : " + command
        data = (command + "\n").encode("utf-8")
        future = asyncio.run_coroutine_threadsafe(
            ble_client.write_gatt_char(UART_CHAR_UUID, data),
            ble_loop
        )
        try:
            future.result()
        except Exception as e:
            self.log_output.text += "\nErreur lors de l'envoi de la commande : " + str(e)


# Application principale
class MainApp(App):
    def build(self):
        return MainScreenManager()


if __name__ == '__main__':
    MainApp().run()
