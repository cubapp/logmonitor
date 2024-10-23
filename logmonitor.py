import os
import time
import logging
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime

# Configuration
# Data and the alarm log is in the /opt/logmonitor directory
KEY_WORD  = "OpenGarageSOMETHING"

# 5 minutes in seconds - wait till the new alarm is send
WAIT_TIME = 300  

#Location of the Route.log from Meshtastic - the file that needs to be scanned for the "KEY_WORD"
LOG_FILE  = "/var/log/DbHl_d150/Router.log" 

#information log about the running process
ALARM_LOG = "/opt/logmonitor/alarm_log.txt"

# Getting Telegram API keys:
# https://core.telegram.org/api/obtaining_api_id
TOKEN     = "MyTELEGRAM_API_TOKEN"
chat_id   = "My_TELEGRAM_ChaT_ID"

# Setup logging for the alarm events
logging.basicConfig(
    filename=ALARM_LOG,
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def alarm(line, timestamp):
    """
    Log the line containing the keyword and its timestamp.

    Args:
        line (str): The line containing the keyword
        timestamp (str): Timestamp when the keyword was found
    """
    logging.info(f"Alarm! Line: {line.strip()}")
    print(f"Alarm triggered at {timestamp}: {line.strip()}")
    message = f"GARAGE Alert Time: {timestamp}: in: {line.strip()}\n"
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message}"
    print(requests.get(url).json()) # this sends the message

class LogFileHandler(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self.last_position = 0
        self.is_waiting = False
        self.last_modified = 0

    def get_file_position(self):
        """Get the current size of the log file."""
        try:
            return os.path.getsize(LOG_FILE)
        except OSError:
            return 0

    def process_new_content(self):
        """Read and process new content in the log file."""
        try:
            with open(LOG_FILE, 'r') as file:
                # Seek to the last known position
                file.seek(self.last_position)

                # Read new content
                new_content = file.read()
                self.last_position = file.tell()

                # Check for keyword
                if KEY_WORD in new_content:
                    # Process each line to find the exact line(s) containing the keyword
                    for line in new_content.splitlines():
                        if KEY_WORD in line:
                            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            alarm(line, timestamp)

                    # Enter waiting period
                    self.is_waiting = True
                    self.last_modified = time.time()
                    #print(f"Entering wait period of {WAIT_TIME} seconds...")

        except Exception as e:
            print(f"Error processing file: {e}")

    def on_modified(self, event):
        """Handle file modification events."""
        if event.src_path.endswith(LOG_FILE):
            current_time = time.time()

            # If we're in waiting period, check if it's over
            if self.is_waiting:
                if current_time - self.last_modified >= WAIT_TIME:
                    #print("Wait period over, resuming monitoring...")
                    self.is_waiting = False
                    self.last_position = self.get_file_position()  # Seek to end
                else:
                    return  # Still in waiting period

            # Process new content if not waiting
            if not self.is_waiting:
                self.process_new_content()
def main():
    # Create an observer and event handler
    observer = Observer()
    event_handler = LogFileHandler()

    # Set initial file position to end of file
    try:
        event_handler.last_position = os.path.getsize(LOG_FILE)
        #print(f"Starting to monitor {LOG_FILE} from position {event_handler.last_position}")
        logging.info(f"Starting to monitor {LOG_FILE} from position {event_handler.last_position}")
    except OSError as e:
        #print(f"Error accessing file: {e}")
        logging.error(f"Error accessing file: {e}")
        return

    # Start monitoring
    observer.schedule(event_handler, path=os.path.dirname(os.path.abspath(LOG_FILE)) or '.',
                     recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        #print("\nMonitoring stopped by user")
        logging.info("Monitoring stopped by user")

    observer.join()

if __name__ == "__main__":
    main()
