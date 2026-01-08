SECRET_PASSWORD = "hi"
MAX_ATTEMPTS = 3


class TronAuth:
    def __init__(self, tron):
        self.tron = tron

    def authenticate(self) -> bool:
        self.tron.speak("Authentication required. Please enter the password.")

        for attempt in range(1, MAX_ATTEMPTS + 1):
            password = input("🔐 Enter password: ").strip()

            print(f"[DEBUG] Typed password: '{password}'")

            if password == SECRET_PASSWORD:
                print("[DEBUG] AUTH SUCCESS — returning True")
                self.tron.speak("Authentication successful. Welcome back.")
                return True

            self.tron.speak(f"Incorrect password. Attempt {attempt} of {MAX_ATTEMPTS}.")

        print("[DEBUG] AUTH FAILED — returning False")
        self.tron.speak("Maximum attempts exceeded. System locked.")
        return False
