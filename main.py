import pygame
import sys
import fourier_file
import lagrange
import scipy
import audio
import numpy as np
import concurrent.futures

'''
    TODO: . https://en.wikipedia.org/wiki/Constrained_optimization
'''
def main_loop():

    # Initialize Pygame
    pygame.init()

    # Initialize the pygame mixer
    bits = -16
    sample_rate = 44100
    pygame.mixer.pre_init(sample_rate, bits)
    pygame.mixer.init(frequency=int(sample_rate * 0.05))
    pygame.mixer.set_num_channels(1)

    # Constants
    WIDTH, HEIGHT = 1280, 720
    LINE_COLOR = (255, 0, 0)  # Red color
    FOURIER_COLOR = (0, 0, 255)  # Blue color
    LINE_THICKNESS = 3
    GRID_COLOR = (100, 100, 100)
    AXIS_COLOR = (0, 0, 100)
    GRID_SPACING = 20
    UI_BOX_COLOR = (200, 200, 200)
    POINT_COLOR = (0, 100, 0)
    GRAPH_HEIGHT_LOWER, GRAPH_HEIGHT_UPPER = (int(HEIGHT / 6), int(5 * HEIGHT / 6))
    GRAPH_WIDTH_LOWER, GRAPH_WIDTH_UPPER = (int(WIDTH / 6), int(5 * WIDTH / 6))
    local_height = (GRAPH_HEIGHT_UPPER - GRAPH_HEIGHT_LOWER) / 2
    SAMPLE_RATE = 20000
    DURATION = 1

    # Screen setup
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Modify Line")

    class Button:
        def __init__(self, texts, y_position):
            button_font = pygame.font.Font(None, 30)
            self.texts = []
            for text in texts:
                self.texts.append(button_font.render(text, True, (0, 0, 0)))
            self.y_position = y_position
            self.box = pygame.Rect(10, y_position, 150, 40)
            self.index = 0

        def toggle_text(self):
            self.index = (self.index + 1) % (len(self.texts))

        def get_state(self):
            return self.index

        def get_text(self):
            return self.texts[self.index]

        # If we are colliding with the box then update it
        def is_colliding(self, position):
            if self.box.collidepoint(position):
                self.toggle_text()
                return True
            return False

        def draw(self):
            pygame.draw.rect(screen, UI_BOX_COLOR, self.box)
            screen.blit(self.get_text(), (20, self.y_position + 10))

        def reset_state(self):
            self.index = 0

    # Useful functions
    def switch_point_to_graph(point: (int, int)) -> (int, int):
        x, y = point
        y = (HEIGHT / 2 - y) / 240
        x = x - GRAPH_WIDTH_LOWER
        x = x * 24
        return (x, y)


    def switch_to_gui(point: (int, int)) -> (int, int):
        x, y = point
        x = (x / 24 + GRAPH_WIDTH_LOWER)
        y = (HEIGHT / 2 - y * 240)
        return (x, y)


    # Line properties
    line_start = [GRAPH_WIDTH_LOWER, int(HEIGHT / 2)]
    line_end = [GRAPH_WIDTH_UPPER, int(HEIGHT / 2)]
    line_points = [line_start, line_end]
    curve_points_gui = [line_start, line_end]
    curve_func = lagrange.build_lagrange([switch_point_to_graph(line_points[index])[0] for index in range(len(line_points))],
                                         [switch_point_to_graph(line_points[index])[1] for index in range(len(line_points))])
    fourier_points_gui = []

    # Returns the y value of the line at the x position
    def line_func(x):
        if isinstance(x, list):  # Check if x is a list
            return [line_func(xi) for xi in x]

        for index in range(len(line_points) - 1):
            if line_points[index][0] < x < line_points[index + 1][0]:
                x1, y1 = line_points[index]
                x2, y2 = line_points[index + 1]
                # calculate y = mx + c
                m = (y2 - y1) / (x2 - x1)
                c = y2 - m * x2
                return m * x + c
        return 0

    # Global States
    change_curve = False
    is_moving_line = False
    play_sound = False
    play_fourier_sound = False
    interpolation_methods = 2
    sound = audio.audio_from_function(line_func, switch_point_to_graph((GRAPH_WIDTH_UPPER, local_height))[0]
                                      - switch_point_to_graph((GRAPH_WIDTH_LOWER, local_height))[0])
    fourier_sound = sound
    fourier_func = fourier_file.fourier_approximation(line_func, [point[0] for point in line_points], 0)

    # UI Buttons
    button_y = 10
    curve_button = Button(["Line", "Lagrange", "Spline"], button_y)
    button_y += 60
    debug_button = Button(["Debug", "Debugging"], button_y)
    button_y += 60
    scale_button = Button(["Scale", "Scaling"], button_y)
    button_y += 60
    fourier_button = Button(["Fourier"] + [str(3*i) for i in range(1,10)], button_y)
    button_y += 60
    distance_button = Button(["Fourier Close", "Fourier Far"], button_y)

    def switch_to_gui_fourier(point: (int, int)) -> (int, int):
        x, y = point
        x = (x / 24 + GRAPH_WIDTH_LOWER)
        if distance_button.get_state() == 0:
            y = (HEIGHT / 2 - y * 240)+local_height-32
        else:
            y = (HEIGHT / 2 - y * 240)+local_height
        return (x, y)

    # Checks if the cursor close enough to the line
    def touching_line(position):
        x, y = position
        # This means that the cursor is close enough to the line
        if abs(y - line_func(x - 5)) < 5 or abs(y - line_func(x + 5)) < 5:
            return True
        else:
            return False


    # Returns if the (x, y) value is within the bounds of the graph
    def within_graph_bounds(position):
        if GRAPH_WIDTH_LOWER <= position[0] <= GRAPH_WIDTH_UPPER and \
                GRAPH_HEIGHT_LOWER <= position[1] <= GRAPH_HEIGHT_UPPER:
            return True
        else:
            return False


    # The value for the cursor position
    font = pygame.font.Font(None, 25)
    position_text = font.render("x: Please move cursor into the graph,"
                                " y: Please move cursor into the graph",
                                True, (100, 0, 0))

    # Main game loop
    running = True
    while running:
        change_curve = False
        screen.fill((255, 255, 255))  # Background color
        for event in pygame.event.get():
            # Update the position of the cursor when the cursor is within the bounds of the graph
            if event.type == pygame.MOUSEMOTION and within_graph_bounds(event.pos):
                font = pygame.font.Font(None, 25)
                graph_point = switch_point_to_graph(event.pos)
                position_text = font.render(f"x: {graph_point[0]}, y: {round(graph_point[1], 2)}", True, (100, 0, 0))
            # Quit the game
            if event.type == pygame.QUIT:
                running = False
            # Add a point to the graph
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    is_moving_line = True
                    # Check if we are touching the buttons and update their states
                    if curve_button.is_colliding(event.pos):
                        change_curve = True
                    debug_button.is_colliding(event.pos)
                    scale_button.is_colliding(event.pos)
                    fourier_state = fourier_button.get_state()
                    fourier_button.is_colliding(event.pos)
                    distance_button.is_colliding(event.pos)
                    if fourier_button.get_state() > 0 and (fourier_button.get_state() != fourier_state or change_curve):
                        # Update fourier
                        if curve_button.get_state() > 0:
                            fourier_func = fourier_file.fourier_approximation(
                                curve_func,
                                np.linspace(0, switch_point_to_graph((GRAPH_WIDTH_UPPER, 0))[0], 10),
                                fourier_button.get_state()*3
                            )
                        else:
                            all_points = line_points + [(point, 0) for point in np.linspace(GRAPH_WIDTH_LOWER, GRAPH_HEIGHT_UPPER, len(line_points)*10)]
                            points = [point[0] for point in all_points]
                            points.sort(reverse=False)
                            fourier_func = fourier_file.fourier_approximation(
                                line_func,
                                points,
                                fourier_button.get_state()*3
                            )
                    elif fourier_button.get_state() == 0:
                        # Clear fourier
                        def waste_func(input_value): return input_value
                        fourier_func = waste_func
                if is_moving_line:
                    # Lazy to convert the line points into a hashmap for O(1)
                    x_value_in_line = False
                    for index in range(len(line_points)):
                        # This is to avoid annoying cases where we need to be precise to edit a point at a certain x value.
                        if abs(event.pos[0] - line_points[index][0]) < 4:
                            line_points[index] = event.pos
                            x_value_in_line = True
                    if not x_value_in_line and within_graph_bounds(event.pos):
                        line_points.append(event.pos)
                        line_points.sort(key=lambda p: p[0])
                    # Reset the sound
                    sound.stop()
                    sound = audio.audio_from_function(line_func,
                                                      switch_point_to_graph((GRAPH_WIDTH_UPPER, local_height))[0]
                                                      - switch_point_to_graph((GRAPH_WIDTH_LOWER, local_height))[0])
            # Reset is_moving_line when we aren't pressing anything
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    is_moving_line = False
            elif event.type == pygame.KEYDOWN:
                # Reset all points when backspace pressed
                if event.key == pygame.K_BACKSPACE:
                    line_points = [line_start, line_end]
                    curve_points = [switch_point_to_graph(line_start), switch_point_to_graph(line_end)]
                    curve_points_gui = [line_start, line_end]
                    curve_func = line_func
                    fourier_button.reset_state()
                    sound.stop()
                    play_sound = False
                    play_fourier_sound = False
                    fourier_sound = sound
                    sound = audio.audio_from_function(line_func, switch_point_to_graph((GRAPH_WIDTH_UPPER, local_height))[0]
                                                      - switch_point_to_graph((GRAPH_WIDTH_LOWER, local_height))[0])
                # Play audio when P is pressed
                elif event.key == pygame.K_p:
                    play_sound = not play_sound
                    if not play_sound:
                        sound.stop()
                    if curve_button.get_state() == 0:
                        sound = audio. \
                            audio_from_function(line_func, switch_point_to_graph((GRAPH_WIDTH_UPPER, local_height))[0]
                                                - switch_point_to_graph((GRAPH_WIDTH_LOWER, local_height))[0])
                    else:
                        sound = audio. \
                            audio_from_function(curve_func, switch_point_to_graph((GRAPH_WIDTH_UPPER, local_height))[0]
                                                - switch_point_to_graph((GRAPH_WIDTH_LOWER, local_height))[0])
                    if play_sound:
                        sound.play(loops=-1)
                elif event.key == pygame.K_f:
                    play_fourier_sound = not play_fourier_sound
                    if not play_fourier_sound:
                        fourier_sound.stop()
                    if play_fourier_sound:
                        fourier_sound.play(loops=-1)
            elif event.type == pygame.VIDEORESIZE:
                width, height = event.size
                if width < WIDTH:
                    width = WIDTH
                if height < HEIGHT:
                    height = HEIGHT
                screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)

        # Draw the Cartesian plane
        # Grid
        for x in range(GRAPH_WIDTH_LOWER, GRAPH_WIDTH_UPPER, GRID_SPACING):
            pygame.draw.line(screen, GRID_COLOR, (x, GRAPH_HEIGHT_LOWER), (x, GRAPH_HEIGHT_UPPER), 1)
        for y in range(GRAPH_HEIGHT_LOWER, GRAPH_HEIGHT_UPPER, GRID_SPACING):
            pygame.draw.line(screen, GRID_COLOR, (GRAPH_WIDTH_LOWER, y), (GRAPH_WIDTH_UPPER, y), 1)
        # Axes
        for x in range(GRAPH_WIDTH_LOWER, GRAPH_WIDTH_UPPER, GRID_SPACING):
            font = pygame.font.Font(None, 14)
            x_text = font.render(f"{round(switch_point_to_graph((x, line_start[1]))[0] / 1000, 1)}", True, (0, 0, 0))
            screen.blit(x_text, (x + 1, line_start[1] + 5))
            pygame.draw.line(screen, AXIS_COLOR, (x, line_start[1]), (x, line_start[1] - 10), 3)
        if debug_button.get_state() == 1:
            for y in range(GRAPH_HEIGHT_LOWER, GRAPH_HEIGHT_UPPER, GRID_SPACING):
                font = pygame.font.Font(None, 14)
                y_text = font.render(f"{switch_to_gui(switch_point_to_graph((line_start[0], y)))[1]}", True, (0, 0, 0))
                screen.blit(y_text, (line_start[0] - 20, y + 1))
                pygame.draw.line(screen, AXIS_COLOR, (line_start[0], y), (line_start[0] + 10, y), 3)
        else:
            for y in range(GRAPH_HEIGHT_LOWER, GRAPH_HEIGHT_UPPER + GRID_SPACING, GRID_SPACING):
                font = pygame.font.Font(None, 14)
                y_text = font.render(f"{round(switch_point_to_graph((line_start[0], y))[1], 2)}", True, (0, 0, 0))
                screen.blit(y_text, (line_start[0] - 20, y + 1))
                pygame.draw.line(screen, AXIS_COLOR, (line_start[0], y), (line_start[0] + 10, y), 3)

        # Draw the curve
        curve_button_state = curve_button.get_state()
        if curve_button_state > 0:
            # If there's an update to the curve
            if is_moving_line or change_curve:
                graph_points = [switch_point_to_graph(point) for point in line_points]
                # Lagrange
                if curve_button_state == 1:
                    curve_func = lagrange.build_lagrange([graph_points[index][0] for index in range(len(graph_points))],
                                                         [graph_points[index][1] for index in range(len(graph_points))])
                # Spline
                elif curve_button_state == 2:
                    curve_func = scipy.interpolate.CubicSpline(
                        [graph_points[index][0] for index in range(len(graph_points))],
                        [graph_points[index][1] for index in range(len(graph_points))])
                points = [(switch_point_to_graph((x, 0))[0], curve_func(switch_point_to_graph((x, 0))[0]))
                          for x in np.linspace(GRAPH_WIDTH_LOWER, GRAPH_WIDTH_UPPER, SAMPLE_RATE)]
                # Reset the sound
                sound.stop()
                sound = audio.audio_from_function(curve_func, switch_point_to_graph((GRAPH_WIDTH_UPPER, local_height))[0]
                                                  - switch_point_to_graph((GRAPH_WIDTH_LOWER, local_height))[0])
                # Switch the curve points from graph points to gui points
                curve_points_gui = [switch_to_gui(point) for point in points]
                output_line = curve_points_gui
            output_line = curve_points_gui
            # Scale mode
            if scale_button.get_state() == 1:
                max_val = max(output_line, key=lambda coord: coord[1])[1]
                min_val = min(output_line, key=lambda coord: coord[1])[1]
                ratio = 1
                if (max_val - min_val) > 0:
                    ratio = (GRAPH_HEIGHT_UPPER - GRAPH_HEIGHT_LOWER) / (max_val - min_val)
                output_line = [
                    (x, GRAPH_HEIGHT_LOWER + ratio * (y - min_val)) for (x, y)
                    in output_line]
            pygame.draw.aalines(screen, LINE_COLOR, False, output_line, LINE_THICKNESS)
        else:
            # Draw the line
            for index in range(len(line_points) - 1):
                pygame.draw.aaline(screen, LINE_COLOR, line_points[index], line_points[index + 1], LINE_THICKNESS)

        # Prepare Fourier
        if fourier_button.get_state() > 0 and (is_moving_line or change_curve):
            if curve_button.get_state() > 0:
                fourier_func = fourier_file.fourier_approximation(
                    curve_func,
                    np.linspace(0, switch_point_to_graph((GRAPH_WIDTH_UPPER, 0))[0], 10),
                    fourier_button.get_state() * 3
                )
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    graph_fourier_points = list(executor.map(lambda x: (x, fourier_func(x)), range(switch_point_to_graph((GRAPH_WIDTH_LOWER, 0))[0],
                                                             switch_point_to_graph((GRAPH_WIDTH_UPPER, 0))[0])))

            else:
                graph_fourier_points = [switch_point_to_graph((x, fourier_func(x))) for x in range(GRAPH_WIDTH_LOWER, GRAPH_WIDTH_UPPER)]

            if scale_button.get_state() == 1:
                max_val = max(graph_fourier_points, key=lambda coord: coord[1])[1]
                min_val = min(graph_fourier_points, key=lambda coord: coord[1])[1]
                ratio = 1
                if (max_val - min_val) > 0:
                    ratio = (GRAPH_HEIGHT_UPPER - GRAPH_HEIGHT_LOWER) / (max_val - min_val)
                graph_fourier_points = [
                    (x, GRAPH_HEIGHT_LOWER + ratio * (y - min_val)) for (x, y)
                    in graph_fourier_points]
            with concurrent.futures.ThreadPoolExecutor() as executor:
                fourier_points_gui = list(
                    executor.map(lambda point: (switch_to_gui_fourier(point)), iter(graph_fourier_points)))
            fourier_sound = audio.audio_from_function(fourier_func, switch_point_to_graph((GRAPH_WIDTH_UPPER, local_height))[0]
                                              - switch_point_to_graph((GRAPH_WIDTH_LOWER, local_height))[0])

        # Draw the fourier approximation
        if fourier_button.get_state() > 0 and len(fourier_points_gui) > 2:
            pygame.draw.aalines(screen, FOURIER_COLOR, False, fourier_points_gui, LINE_THICKNESS)

        # Draw the points pressed:
        for point in line_points:
            pygame.draw.circle(screen, POINT_COLOR, point, 5)
        # Draw the UI:
        curve_button.draw()
        debug_button.draw()
        scale_button.draw()
        fourier_button.draw()
        distance_button.draw()

        # Render the cursor position
        screen.blit(position_text, (GRAPH_WIDTH_LOWER, HEIGHT - 40))

        # Render the help text
        font = pygame.font.Font(None, 20)
        help_text = font.render("Press \"P\" to play sound, \"F\" to play fourier sound,"
                                " and \"BACKSPACE\" to clear the chart before changing settings", True, (0, 100, 0))
        screen.blit(help_text, (GRAPH_WIDTH_LOWER, HEIGHT - 80))

        # Update the display
        pygame.display.flip()

    # Quit Pygame
    pygame.quit()
    sys.exit()


def main():
    main_loop()

if __name__ == "__main__":
    main()
