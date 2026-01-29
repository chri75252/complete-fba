
import sys
from PIL import Image

def extract_metadata(image_path):
    try:
        with Image.open(image_path) as img:
            print(f"Format: {img.format}")
            print(f"Mode: {img.mode}")
            print(f"Size: {img.size}")
            
            print("\n--- Info Dictionary ---")
            for k, v in img.info.items():
                print(f"{k}: {v}")
                
            # Specifically check for 'parameters' (often used by Stable Diffusion)
            if 'parameters' in img.info:
                print("\n--- Parameters ---")
                print(img.info['parameters'])
                
            # Check for text chunks if not in info
            if hasattr(img, 'text'):
                print("\n--- Text Chunks ---")
                for k, v in img.text.items():
                    print(f"{k}: {v}")
                    
    except Exception as e:
        print(f"Error reading metadata: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        extract_metadata(sys.argv[1])
    else:
        print("Please provide an image path.")
