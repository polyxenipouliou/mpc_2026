import os

from manim import *


class Introduction(Scene):
    def construct(self):
        # Add title text
        title = Text("Welcome to our survey!", font_size=48, color=BLUE)
        self.play(Write(title))
        self.wait(1)
        self.play(FadeOut(title))

        # Add subtitle
        subtitle = MarkupText(
            'Let\'s test your <span fgcolor="yellow">J</span>ust '
            '<span fgcolor="yellow">N</span>oticeable '
            '<span fgcolor="yellow">D</span>ifference in frequency',
            font_size=36
        )
        self.play(Write(subtitle))
        self.wait(3)

        # Fade out text
        self.play(FadeOut(subtitle))

        title = Text("In each audio clip, you will hear 8 impulses;\nthey are arranged as 4 pairs.", font_size=26,
                     color=BLUE)
        self.play(FadeIn(title))
        self.wait(5)
        self.play(FadeOut(title))

        title = Text(
            "Please choose the one you think is higher in pitch for each pair.\n",
            font_size=26, color=BLUE)
        self.play(FadeIn(title))
        self.wait(3)
        self.play(FadeOut(title))

        title = Text(
            "A pair may sound like this:",
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
    scene = Introduction()
    scene.render()

    print(f"Video saved to: {os.path.join(output_directory, 'MyScene.mp4')}")