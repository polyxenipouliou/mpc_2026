from manim import *
import os


class WholeAudio(Scene):
    def construct(self):
        # No boxes or grid lines - pure horizontal lines and text
        screen_width = config.frame_width
        screen_height = config.frame_height

        # Calculate section dimensions (top half for lines, bottom half for text)
        top_half_height = screen_height / 2
        col_width = screen_width / 4

        # Top row y-positions (within top half)
        top_row_y_high = top_half_height * 0.75  # 3/4 down from top
        top_row_y_low = top_half_height * 0.25  # 1/4 down from top

        # Bottom text position (center of bottom half)
        bottom_text_y = -top_half_height / 2

        # Define patterns for each column
        patterns = [
            ("high", "low"),  # 高 - 低
            ("low", "high"),  # 低 - 高
            ("low", "high"),  # 高 - 高（相等）
            ("high", "low")  # 低 - 低（相等）
        ]

        # Draw horizontal lines in top half (no boxes)
        for j, pattern in enumerate(patterns):
            # Column boundaries
            left_x = -screen_width / 2 + j * col_width
            right_x = left_x + col_width

            # Left half center
            left_center_x = left_x + col_width / 4
            # Right half center
            right_center_x = left_x + 3 * col_width / 4

            # Determine line heights
            left_y = top_row_y_high if pattern[0] == "high" else top_row_y_low
            right_y = top_row_y_high if pattern[1] == "high" else top_row_y_low

            # Create left line (width = col_width/4)
            left_line = Line(
                start=(left_center_x - col_width / 8, left_y, 0),
                end=(left_center_x + col_width / 8, left_y, 0),
                color=YELLOW,
                stroke_width=4
            )

            # Create right line (width = col_width/4)
            right_line = Line(
                start=(right_center_x - col_width / 8, right_y, 0),
                end=(right_center_x + col_width / 8, right_y, 0),
                color=YELLOW,
                stroke_width=4
            )

            # Animate lines one by one
            self.play(Create(left_line), run_time=0.3)
            self.play(Create(right_line), run_time=0.3)
            self.wait(0.3)  # 300ms pause between patterns

        # Create text for bottom half AFTER lines are complete
        bottom_texts = VGroup()
        texts = ["First", "Second", "Second", "First"]
        for j in range(4):
            x_pos = -screen_width / 2 + j * col_width + col_width / 2
            text = Text(texts[j], font_size=24, color=YELLOW)
            text.move_to([x_pos, bottom_text_y, 0])
            bottom_texts.add(text)

        # Display text at the end
        self.play(Write(bottom_texts))

        # Final wait
        self.wait(2)


if __name__ == "__main__":
    # Set output directory
    output_directory = os.path.join("output", "videos")
    os.makedirs(output_directory, exist_ok=True)

    # Render configuration
    config.media_dir = output_directory
    config.quality = "production_quality"
    config.format = "mp4"

    scene = WholeAudio()
    scene.render()

    print(f"Video saved to: {os.path.join(output_directory, 'WholeAudio.mp4')}")
