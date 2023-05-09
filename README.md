# Keylogger

## Introduction:

This Python script functions as a comprehensive keylogger, proficient in capturing keyboard inputs, mouse movements, screen captures, and audio recordings of the computer user. Additionally, it facilitates the transfer of captured data to a specified email address at predetermined .

## Requirements:

The script requires Python version 3.x and the following Python libraries:
- `pynput`
- `PIL`
- `pyaudio`
- `cv2`
- `wave`
- `smtplib`
- `logging`
## Installation:

Install the required Python libraries using pip. The following command can be used:
```python
pip install pynput PIL pyaudio opencv-python wave smtplib
```

## Usage:

To use the script, follow the steps below:

- Open the terminal or command prompt on your computer.
- Navigate to the directory where the script is saved.
Run the following command:
```python
python keylogger.py
```

The script will start running, and it will capture the user's keyboard inputs, mouse movements, and screen captures.
The script will send an email with the captured data to a specified email address at regular intervals.

## Configuration:

The Keylogger object has the following parameters:
- `max_count`: The maximum number of keys to log before writing to the log file. The default value is `10`.
- `log_file`: The name of the file to write the log to. The default value is `"log.txt"`.
- `interval`: The interval in seconds at which to capture the screen and record audio. The default value is `60`.
- `idle_time`: The amount of time in seconds after which to consider the user as idle. The default value is `300`.
- `SMTP_SERVER`: The `SMTP` server to use for sending emails. The default value is `'smtp.gmail.com'`.
- `SMTP_PORT`: The `SMTP` port to use for sending emails. The default value is `587`.
- `SMTP_USERNAME`: The email address to use for sending emails. This must be a Gmail account.
- `SMTP_PASSWORD`: The password for the Gmail account.

The Keylogger object has the following methods:
- `on_press`: This method logs a pressed key and performs periodic screen captures, audio recordings, and email sends.
- `check_idle`: This method checks if the user is idle.
- `stop_listening`: This method releases the video capture and video writer resources, if they exist, and then calls the superclass's stop_listening method.
- `on_move`: This method handles a mouse move event.

## Troubleshooting:

If the script encounters an error, it will write the error message to the `error.log` file.

## License:

This project is licensed under the MIT License. See the [LICENSE](https://github.com/TheHumanoidTyphoon/keylogger/blob/master/LICENSE) file for details.
