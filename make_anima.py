from manim import *
import random

# Parameter definitions
FREQ_A = 500  # Example frequency A (Hz)
FREQ_B = 880  # Example frequency B (Hz)
NUM_SEGMENTS = 4  # Total number of segments


class AudioVisualization(Scene):
    def construct(self):
        # Add title and description
        title = Text("Frequency Playback Visualization", font_size=40).to_edge(UP)
        self.play(Write(title))

        explanation = (
            Text(
                "Each line represents the trend of frequency change during audio playback.\n"
                "Upward lines indicate increasing frequency; downward lines indicate decreasing frequency.",
                font_size=24,
            )
            .next_to(title, DOWN)
            .shift(DOWN * 0.5)
        )
        self.play(Write(explanation), run_time=3)
        self.wait(1)

        # Explain JND-related concepts
        jnd_explanation = (
            Text(
                "This test helps determine the Just Noticeable Difference (JND)\n"
                "in human auditory perception between frequencies.",
                font_size=24,
                color=YELLOW,
            )
            .next_to(explanation, DOWN)
            .shift(DOWN * 0.5)
        )
        self.play(Write(jnd_explanation), run_time=3)
        self.wait(2)

        # Create axes
        axes = Axes(
            x_range=[0, NUM_SEGMENTS + 1, 1],
            y_range=[0, 2, 1],
            axis_config={"color": BLUE},
            x_length=10,
            y_length=4,
        ).shift(DOWN * 1)
        self.play(Create(axes))

        # Label X and Y axes
        x_label = axes.get_x_axis_label("Segment Index").shift(RIGHT * 4)
        y_label = axes.get_y_axis_label("Frequency Level").shift(UP * 2)
        self.play(Write(x_label), Write(y_label))

        # Dynamically draw trend lines
        random.seed(42)  # Fixed random seed for reproducibility
        start_point = axes.c2p(0, 1)  # Starting point
        current_x = 0
        previous_y = 1

        for i in range(NUM_SEGMENTS):
            # Randomly decide frequency order
            freq_order = random.choice([(FREQ_A, FREQ_B), (FREQ_B, FREQ_A)])
            freq_1, freq_2 = freq_order

            # Calculate trend: upward or downward
            if freq_1 < freq_2:
                next_y = previous_y + 0.5  # Upward
            else:
                next_y = previous_y - 0.5  # Downward

            # Get coordinates of the next point
            end_point = axes.c2p(current_x + 1, next_y)

            # Draw trend line
            trend_line = Line(start_point, end_point, color=RED if freq_1 < freq_2 else GREEN)
            self.play(Create(trend_line), run_time=1)

            # Update current point and coordinates
            start_point = end_point
            current_x += 1
            previous_y = next_y

        # Concluding text
        conclusion = (
            Text("This visualization helps you understand how frequencies change.", font_size=28, color=ORANGE)
            .next_to(axes, DOWN)
            .shift(DOWN * 0.5)
        )
        self.play(Write(conclusion))
        self.wait(2)


# Main function
if __name__ == "__main__":
    # Run Manim rendering
    scene = AudioVisualization()
    scene.render()