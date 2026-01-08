import os
import datetime
import requests
from io import BytesIO
from PIL import Image
from dotenv import dotenv_values

# ===============================
# LOAD ENV
# ===============================
env = dotenv_values(".env")
HF_API_KEY = env.get("HF_API_KEY")

if not HF_API_KEY:
    raise RuntimeError("HF_API_KEY not found in .env file")

# ===============================
# IMAGE GENERATOR
# ===============================
class HFImageGenerator:
    def __init__(self):
        self.model_url = (
            "https://api-inference.huggingface.co/models/"
            "runwayml/stable-diffusion-v1-5"
        )
        self.headers = {
            "Authorization": f"Bearer {HF_API_KEY}"
        }

        self.output_dir = os.path.join(
            os.path.expanduser("~"),
            "Downloads",
            "tron_images"
        )
        os.makedirs(self.output_dir, exist_ok=True)

    def generate(self, prompt):
        response = requests.post(
            self.model_url,
            headers=self.headers,
            json={"inputs": prompt},
            timeout=120
        )

        if response.status_code != 200:
            raise RuntimeError(
                f"Hugging Face error {response.status_code}: {response.text}"
            )

        image = Image.open(BytesIO(response.content))

        filename = (
            "image_"
            + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            + ".png"
        )
        path = os.path.join(self.output_dir, filename)

        image.save(path)
        return path