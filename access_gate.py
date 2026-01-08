from face_auth import verify_face
from voice_auth import verify_voice

def tron_access():
    print("🔒 TRON Locked")

    if not verify_face():
        print("❌ Face not recognized")
        return False

    print("👁️ Face verified")

    if not verify_voice():
        print("❌ Voice phrase rejected")
        return False

    print("🟢 ACCESS GRANTED — Welcome back")
    return True


if __name__ == "__main__":
    if tron_access():
        print("🤖 TRON ONLINE")
    else:
        print("🔴 ACCESS DENIED")