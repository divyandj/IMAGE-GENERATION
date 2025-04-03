import base64
import os
import mimetypes
import time
from google import genai
from google.genai import types

class ImageGenerator:
    @staticmethod
    def save_binary_file(file_name, data):
        f = open(file_name, "wb")
        f.write(data)
        f.close()
        return file_name

    @staticmethod
    def generate_image(prompt):
        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

        model = "gemini-2.0-flash-exp-image-generation"
        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)],
            ),
        ]
        generate_content_config = types.GenerateContentConfig(
            response_modalities=["image", "text"],
            response_mime_type="text/plain",
        )

        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        ):
            if not chunk.candidates or not chunk.candidates[0].content or not chunk.candidates[0].content.parts:
                continue
            if chunk.candidates[0].content.parts[0].inline_data:
                timestamp = int(time.time())
                file_name = f"generated_image_{timestamp}"
                inline_data = chunk.candidates[0].content.parts[0].inline_data
                file_extension = mimetypes.guess_extension(inline_data.mime_type) or ".png"
                full_file_name = f"{file_name}{file_extension}"
                saved_path = ImageGenerator.save_binary_file(full_file_name, inline_data.data)
                print(f"File of mime type {inline_data.mime_type} saved to: {saved_path}")
                return saved_path, prompt
            else:
                print(chunk.text)
        return None, None

    @staticmethod
    def modify_image(original_image_path, original_prompt, modification_prompt):
        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

        if not os.path.exists(original_image_path):
            raise FileNotFoundError(f"Original image not found at {original_image_path}")
        with open(original_image_path, "rb") as f:
            image_data = f.read()
        mime_type = mimetypes.guess_type(original_image_path)[0] or "image/png"

        combined_prompt = f"{original_prompt}, modified to {modification_prompt}"
        model = "gemini-2.0-flash-exp-image-generation"
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=combined_prompt),
                    types.Part.from_inline_data(data=image_data, mime_type=mime_type)
                ],
            ),
        ]
        generate_content_config = types.GenerateContentConfig(
            response_modalities=["image", "text"],
            response_mime_type="text/plain",
        )

        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        ):
            if not chunk.candidates or not chunk.candidates[0].content or not chunk.candidates[0].content.parts:
                continue
            if chunk.candidates[0].content.parts[0].inline_data:
                timestamp = int(time.time())
                file_name = f"modified_image_{timestamp}"
                inline_data = chunk.candidates[0].content.parts[0].inline_data
                file_extension = mimetypes.guess_extension(inline_data.mime_type) or ".png"
                full_file_name = f"{file_name}{file_extension}"
                saved_path = ImageGenerator.save_binary_file(full_file_name, inline_data.data)
                print(f"Modified file of mime type {inline_data.mime_type} saved to: {saved_path}")
                return saved_path, combined_prompt
            else:
                print(chunk.text)
        return None, None

    @staticmethod
    def generate_story(story_prompt, num_images):
        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

        model = "gemini-2.0-flash-exp-image-generation"
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(
                        text=f"Generate a story about '{story_prompt}'. Start with a brief introduction, "
                             f"then provide exactly {num_images} numbered scenes. Each scene should be a concise "
                             "paragraph suitable for generating an image in a 3D cartoon animation style. "
                             "For each scene, generate an image. Format the output as:\n"
                             "Introduction: [text]\n"
                             "Scene 1: [text]\n"
                             "Scene 2: [text]\n"
                             "..."
                    ),
                ],
            ),
        ]
        generate_content_config = types.GenerateContentConfig(
            response_modalities=["image", "text"],
            response_mime_type="text/plain",
        )

        # Process the streaming response
        story_text = ""
        image_paths = []
        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        ):
            if not chunk.candidates or not chunk.candidates[0].content or not chunk.candidates[0].content.parts:
                continue
            if chunk.candidates[0].content.parts[0].inline_data:
                timestamp = int(time.time())
                file_name = f"story_image_{timestamp}"
                inline_data = chunk.candidates[0].content.parts[0].inline_data
                file_extension = mimetypes.guess_extension(inline_data.mime_type) or ".png"
                full_file_name = f"{file_name}{file_extension}"
                saved_path = ImageGenerator.save_binary_file(full_file_name, inline_data.data)
                print(f"Story image of mime type {inline_data.mime_type} saved to: {saved_path}")
                image_paths.append(saved_path)
            else:
                story_text += chunk.text

        # Debugging output
        print(f"Debug: Raw story text:\n{story_text}")
        print(f"Debug: Image paths: {image_paths}")

        # Parse the story text into introduction and scenes
        lines = story_text.strip().split('\n')
        introduction = ""
        scenes = []
        current_scene = None

        for line in lines:
            line = line.strip()
            if not line:  # Skip empty lines
                continue
            if line.startswith("Introduction:"):
                introduction = line.replace("Introduction:", "").strip()
            elif line.startswith("Scene"):
                if current_scene:
                    scenes.append(current_scene)
                current_scene = line
            elif current_scene:
                current_scene += " " + line

        if current_scene:
            scenes.append(current_scene)

        # Debugging parsed scenes
        print(f"Debug: Parsed scenes: {scenes}")

        # Ensure we have the correct number of scenes and images
        scenes = scenes[:num_images]
        image_paths = image_paths[:num_images]

        # Build the result
        story_result = {'introduction': introduction, 'scenes': []}
        for i, scene in enumerate(scenes):
            scene_text = scene.split(':', 1)[1].strip() if ':' in scene else scene
            image_path = image_paths[i] if i < len(image_paths) else None
            story_result['scenes'].append({
                'text': scene_text,
                'path': image_path,
                'prompt': f"{scene_text}, in a 3D cartoon animation style"
            })

        return story_result

if __name__ == "__main__":
    if "GEMINI_API_KEY" not in os.environ:
        print("Error: GEMINI_API_KEY environment variable not set")
    else:
        story_result = ImageGenerator.generate_story(
            "a white baby goat going on an adventure in a farm in a 3d cartoon animation style",
            3
        )
        print(f"Introduction: {story_result['introduction']}")
        for scene in story_result['scenes']:
            print(f"{scene['text']}\nGenerated Image {scene['path']}")