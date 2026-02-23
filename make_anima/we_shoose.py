import os

from manim import *

class WeChoose(Scene):
    def construct(self):
        title = Text(
            "In this case, we choose \"Second\" because it is higher",
            font_size=26, color=BLUE)
        self.play(FadeIn(title))
        self.wait(3)
        self.play(FadeOut(title))
        title = Text(
            "Here's what an audio file looks like:",
            font_size=26, color=BLUE)
        self.play(FadeIn(title))
        self.wait(3)
        self.play(FadeOut(title))

if __name__ == "__main__":
    # Define output path
    output_directory = os.path.join("output", "videos")
    os.makedirs(output_directory, exist_ok=True)  # Ensure directory exists

    # Configure Manim rendering parameters
    config.media_dir = output_directory
    config.quality = "production_quality"  # Rendering quality (low, medium, high)
    config.format = "mp4"  # Output format (mp4, gif, etc.)

    # Manually trigger rendering
    scene = WeChoose()
    scene.render()

    print(f"Video saved to: {os.path.join(output_directory, 'WeChoose.mp4')}")