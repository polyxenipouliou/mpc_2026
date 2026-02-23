import os

from manim import *


class TwoSineWaves(Scene):
    def construct(self):
        # Define sine wave parameters
        amplitude = 20.0  # Amplitude

        # Create axes
        axes_top = Axes(
            x_range=[0, 6, 1],  # X-axis range: 0 to 6 seconds
            y_range=[-amplitude * 1.5, amplitude * 1.5, amplitude],  # Y-axis range
            x_length=10,  # X-axis length (width on screen)
            y_length=3,  # Y-axis length (height on screen)
            axis_config={"color": BLUE},
        ).to_edge(UP, buff=0.5)  # Position axes at the top of the screen

        axes_bottom = Axes(
            x_range=[0, 6, 1],  # X-axis range: 0 to 6 seconds
            y_range=[-amplitude * 1.5, amplitude * 1.5, amplitude],  # Y-axis range
            x_length=10,  # X-axis length (width on screen)
            y_length=3,  # Y-axis length (height on screen)
            axis_config={"color": BLUE},
        ).to_edge(DOWN, buff=0.5)  # Position axes at the bottom of the screen

        # Add axis labels
        x_label_top = axes_top.get_x_axis_label("Time (s)")
        y_label_top = axes_top.get_y_axis_label("Amplitude")
        x_label_bottom = axes_bottom.get_x_axis_label("Time (s)")
        y_label_bottom = axes_bottom.get_y_axis_label("Amplitude")

        # self.add(axes_top, x_label_top, y_label_top)
        # self.add(axes_bottom, x_label_bottom, y_label_bottom)

        # Define sine wave function
        def sine_wave(x, time_offset, frequency):
            return amplitude * np.sin(2 * np.pi * frequency * (x - time_offset))

        # Create the top sine wave graph
        graph_top = axes_top.plot(
            lambda x: sine_wave(x, time_offset=0, frequency=3),
            x_range=[0, 6, 0.01],
            color=YELLOW
        )

        # Create the bottom sine wave graph
        graph_bottom = axes_bottom.plot(
            lambda x: sine_wave(x, time_offset=0, frequency=5),
            x_range=[0, 6, 0.01],
            color=GREEN
        )

        # Dynamically update the top sine wave
        def update_graph_top(mob, dt):
            if self.time < 3:  # Update only during the first 3 seconds
                mob.become(
                    axes_top.plot(
                        lambda x: sine_wave(x, time_offset=self.time, frequency=3),
                        x_range=[0, 6, 0.01],
                        color=YELLOW
                    )
                )

        # Dynamically update the bottom sine wave
        def update_graph_bottom(mob, dt):
            if 3 <= self.time < 6:  # Update between 3 and 6 seconds
                mob.become(
                    axes_bottom.plot(
                        lambda x: sine_wave(x, time_offset=self.time - 3, frequency=5),
                        x_range=[0, 6, 0.01],
                        color=GREEN
                    )
                )

        # Add descriptive text
        text_top = Text("First ", font_size=24, color=YELLOW).next_to(axes_top, RIGHT)
        text_bottom = Text("Second ", font_size=24, color=GREEN).next_to(axes_bottom, RIGHT)

        # Add updaters
        graph_top.add_updater(update_graph_top)
        graph_bottom.add_updater(update_graph_bottom)

        # Add all elements to the scene
        self.add(graph_top, text_top)

        # Wait for animation to run for 3 seconds
        self.wait(3)

        self.add(graph_bottom, text_bottom)
        self.wait(3)

        self.remove(graph_top, text_top, graph_bottom, text_bottom)

        # Stop animation
        graph_top.remove_updater(update_graph_top)
        graph_bottom.remove_updater(update_graph_bottom)


if __name__ == "__main__":
    # Define output path
    output_directory = os.path.join("output", "videos")
    os.makedirs(output_directory, exist_ok=True)  # Ensure directory exists

    # Configure Manim rendering parameters
    config.media_dir = output_directory
    config.quality = "high_quality"  # Rendering quality (low, medium, high)
    config.format = "mp4"  # Output format (mp4, gif, etc.)

    # Manually trigger rendering
    scene = TwoSineWaves()
    scene.render()

    print(f"Video saved to: {os.path.join(output_directory, 'MyScene.mp4')}")