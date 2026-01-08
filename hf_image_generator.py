import os
import datetime
import replicate
import requests
from io import BytesIO
from PIL import Image
from dotenv import dotenv_values

# ===============================
# LOAD ENV
# ===============================
env = dotenv_values(".env")
REPLICATE_API_TOKEN = env.get("REPLICATE_API_TOKEN")

if not REPLICATE_API_TOKEN:
    raise RuntimeError("❌ REPLICATE_API_TOKEN not found in .env")

os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN

# ===============================
# IMAGE GENERATOR
# ===============================
class ReplicateImageGenerator:
    def __init__(self):
        self.output_dir = os.path.join(
            os.path.expanduser("~"),
            "Downloads",
            "tron_images"
        )
        os.makedirs(self.output_dir, exist_ok=True)

        # ✅ Load model object properly
        self.model = replicate.models.get("stability-ai/sdxl")
        self.version = self.model.versions.list()[0]  # latest version

    def generate(self, prompt: str) -> str:
        print("🎨 Generating image (Replicate Free Tier)...")

        output = replicate.run(
            self.version,
            input={
                "prompt": prompt,
                "width": 1024,
                "height": 1024,
                "num_outputs": 1,
                "num_inference_steps": 30,
                "guidance_scale": 7.5
            }
        )

        image_url = output[0]
        image_data = requests.get(image_url).content
        image = Image.open(BytesIO(image_data)).convert("RGB")

        filename = "image_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + ".png"
        path = os.path.join(self.output_dir, filename)

        image.save(path)
        return path


# ===============================
# STANDALONE RUN
# ===============================
if __name__ == "__main__":
    print("🧠 TRON – Replicate Image Generator (WORKING)")
    print("Type a prompt. Type 'exit' to quit.\n")

    generator = ReplicateImageGenerator()

    while True:
        prompt = input("🖼️ Prompt > ").strip()
        if prompt.lower() in ("exit", "quit"):
            break
        if not prompt:
            continue

        try:
            path = generator.generate(prompt)
            print(f"✅ Image saved at:\n{path}\n")
        except Exception as e:
            print(f"❌ Error: {e}\n")
