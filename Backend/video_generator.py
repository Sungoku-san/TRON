import os
import time
import datetime
import requests
from dotenv import dotenv_values

# ===============================
# LOAD ENV
# ===============================
env = dotenv_values(".env")
RUNWAY_API_KEY = env.get("RUNWAY_API_KEY")

if not RUNWAY_API_KEY:
    raise RuntimeError("RUNWAY_API_KEY not found in .env")

# ===============================
# VIDEO GENERATOR
# ===============================
class VideoGenerator:
    def __init__(self):
        self.base_url = "https://api.runwayml.com/v1"
        self.headers = {
            "Authorization": f"Bearer {RUNWAY_API_KEY}",
            "Content-Type": "application/json"
        }

        self.output_dir = os.path.join(
            os.path.expanduser("~"),
            "Downloads",
            "tron_videos"
        )
        os.makedirs(self.output_dir, exist_ok=True)

    def generate(self, prompt, seconds=4):
        # 1️⃣ Create generation job
        response = requests.post(
            f"{self.base_url}/image_to_video",
            headers=self.headers,
            json={
                "prompt": prompt,
                "duration": seconds
            }
        )

        if response.status_code != 200:
            raise RuntimeError(f"Video job creation failed: {response.text}")

        job_id = response.json()["id"]

        # 2️⃣ Poll until ready
        video_url = self._wait_for_completion(job_id)

        # 3️⃣ Download video
        return self._download_video(video_url)

    def _wait_for_completion(self, job_id):
        while True:
            status = requests.get(
                f"{self.base_url}/tasks/{job_id}",
                headers=self.headers
            ).json()

            if status.get("status") == "completed":
                return status["output"]["video"]

            if status.get("status") == "failed":
                raise RuntimeError("Video generation failed")

            time.sleep(5)

    def _download_video(self, url):
        video_data = requests.get(url).content

        filename = (
            "video_"
            + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            + ".mp4"
        )
        path = os.path.join(self.output_dir, filename)

        with open(path, "wb") as f:
            f.write(video_data)

        return path