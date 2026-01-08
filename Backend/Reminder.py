import threading
import time
import tkinter as tk
from tkinter import messagebox
import re

class Reminder:
    def __init__(self):
        self.reminders = []

    # -----------------------------
    # PUBLIC METHOD
    # -----------------------------
    def set_reminder(self, text):
        """
        Example inputs:
        - "remind me to drink water in 30 minutes"
        - "remind me to call mom in 10 seconds"
        - "remind me to study in 2 hours"
        """

        parsed = self._parse_text(text)
        if not parsed:
            return False, "Could not understand reminder time."

        message, delay = parsed

        thread = threading.Thread(
            target=self._reminder_thread,
            args=(message, delay),
            daemon=True
        )
        thread.start()

        self.reminders.append((message, delay))
        return True, f"Reminder set for {message}"

    # -----------------------------
    # TEXT PARSER
    # -----------------------------
    def _parse_text(self, text):
        text = text.lower()

        # Extract message
        msg_match = re.search(r"remind me to (.+?) in", text)
        if not msg_match:
            return None

        message = msg_match.group(1)

        # Extract time
        time_match = re.search(r"in (\d+)\s*(second|seconds|minute|minutes|hour|hours)", text)
        if not time_match:
            return None

        value = int(time_match.group(1))
        unit = time_match.group(2)

        if "second" in unit:
            delay = value
        elif "minute" in unit:
            delay = value * 60
        elif "hour" in unit:
            delay = value * 3600
        else:
            return None

        return message, delay

    # -----------------------------
    # BACKGROUND TIMER
    # -----------------------------
    def _reminder_thread(self, message, delay):
        time.sleep(delay)
        self._show_popup(message)

    # -----------------------------
    # POPUP
    # -----------------------------
    def _show_popup(self, message):
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo("🔔 TRON Reminder", f"Reminder:\n\n{message}")
        root.destroy()