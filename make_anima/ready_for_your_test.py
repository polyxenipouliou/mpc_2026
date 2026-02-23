import os

from manim import *

class Ready(Scene):
    def construct(self):
        final_text = Text("Ready for Your Test?", font="Arial", font_size=74, color="#FFD93D")

        # Add glow effect animation
        glow_effect = final_text.copy()
        glow_effect.set_stroke("#FFD93D", 10, opacity=0.8)

        self.play(
            Write(final_text),
            ShowPassingFlash(glow_effect),
            run_time=2
        )

        self.wait(3)

        # Fade out at the end
        self.play(
            *[FadeOut(mob) for mob in self.mobjects],
            run_time=2
        )

if __name__ == "__main__":
    # Define output path
    output_directory = os.path.join("output", "videos")
    os.makedirs(output_directory, exist_ok=True)  # Ensure directory exists

    # Configure Manim rendering parameters
    config.media_dir = output_directory
    config.quality = "production_quality"  # Rendering quality (low, medium, high)
    config.format = "mp4"  # Output format (mp4, gif, etc.)

    # Manually trigger rendering
    scene = Ready()
    scene.render()

    print(f"Video saved to: {os.path.join(output_directory, 'MyScene.mp4')}")