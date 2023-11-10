import pygame
import sys
import math
import lagrange
import scipy
import audio
import numpy as np

'''
    TODO: . Add the functionality to limit the number of constants in the fft approximation.
          . Figure out how to compile this code to become like an exe file.
          . How to save the produced sound.
          . H to show the help menu
          . Scale graph with button to decide
          . Hermite curve
          . Input whitenoise to produce sound
          . https://en.wikipedia.org/wiki/Constrained_optimization
'''

# Calculate the slopes such that they are continuous. At the end you should be getting a big matrix

# Initialize Pygame
pygame.init()
# Initialize the pygame mixer
bits = -16
sample_rate = 44100
pygame.mixer.pre_init(sample_rate, bits)
pygame.mixer.init(frequency=int(sample_rate*0.05))
pygame.mixer.set_num_channels(1)
print(f"Pygame mixer init: {pygame.mixer.get_init()}")

# Constants
WIDTH, HEIGHT = 1280, 720
LINE_COLOR = (255, 0, 0)  # Red color
LINE_THICKNESS = 3
GRID_COLOR = (100, 100, 100)
AXIS_COLOR = (0, 0, 100)
GRID_SPACING = 20
UI_BOX_COLOR = (200, 200, 200)
POINT_COLOR = (0, 100, 0)
GRAPH_HEIGHT_LOWER, GRAPH_HEIGHT_UPPER = (int(HEIGHT / 6), int(5 * HEIGHT / 6))
GRAPH_WIDTH_LOWER, GRAPH_WIDTH_UPPER = (int(WIDTH / 6), int(5 * WIDTH / 6))

# Screen setup
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Modify Line")

# class button:
#     def __init__(self, text, y_position, onclick_event):
#         text = text
#

# Useful functions
def switch_point_to_graph(point: (int, int)) -> (int, int):
    x, y = point
    y = (HEIGHT/2 - y)/240
    x = x - GRAPH_WIDTH_LOWER
    x = x*24
    return (x, y)

def switch_to_gui(point: (int, int)) -> (int, int):
    x, y = point
    x = (x/24 + GRAPH_WIDTH_LOWER)
    y = (HEIGHT/2 - y*240)
    return (x, y)

# Line properties
line_start = [GRAPH_WIDTH_LOWER, int(HEIGHT / 2)]
line_end = [GRAPH_WIDTH_UPPER, int(HEIGHT / 2)]
line_points = [line_start, line_end]
curve_points = [switch_point_to_graph(line_start), switch_point_to_graph(line_end)]
curve_points_gui = [line_start, line_end]
graph_points = [switch_point_to_graph(point) for point in line_points]
curve_func = lagrange.build_lagrange([graph_points[index][0] for index in range(len(graph_points))],
                                     [graph_points[index][1] for index in range(len(graph_points))])
is_dragging_start = False
is_dragging_end = False
is_moving_line = False
draw_curve = 0
interpolation_methods = 2

# UI properties
ui_box = pygame.Rect(10, 10, 150, 40)
debug_box = pygame.Rect(10, 70, 150, 40)
scale_box = pygame.Rect(10, 130, 150, 40)
font = pygame.font.Font(None, 30)
curve_text = font.render("Curve", True, (0, 0, 0))
lagrange_text = font.render("Lagrange", True, (0, 0, 0))
spline_text = font.render("Spline", True, (0, 0, 0))
line_text = font.render("Line", True, (0, 0, 0))
debug_text = font.render("Debug", True, (0, 0, 0))
debugging_text = font.render("Debugging", True, (0, 0, 0))
scale_text = font.render("Scale", True, (0, 0, 0))
scaling_text = font.render("Scaling", True, (0, 0, 0))
debug_mode = False
change_curve = False
scale_mode = False

# Returns the y value of the line at the x position
# TODO: Maybe make this into GUI vs graph
def line_func(x):
    for index in range(len(line_points) - 1):
        if line_points[index][0] < x < line_points[index + 1][0]:
            x1, y1 = line_points[index]
            x2, y2 = line_points[index + 1]
            # calculate y = mx + c
            m = (y2 - y1) / (x2 - x1)
            c = y2 - m * x2
            return m * x + c
    return 0

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
            position_text = font.render(f"x: {graph_point[0]}, y: {round(graph_point[1],2)}", True, (100, 0, 0))
        # Quit the game
        if event.type == pygame.QUIT:
            running = False
        # Add a point to the graph
        elif event.type == pygame.MOUSEBUTTONDOWN:
            print(f"[DEBUG] Mouse button down: {event.pos}")
            if event.button == 1:
                is_moving_line = True
                if ui_box.collidepoint(event.pos):
                    draw_curve = (draw_curve+1) % (interpolation_methods+1)
                    change_curve = True
                elif debug_box.collidepoint(event.pos):
                    debug_mode = not debug_mode
                elif scale_box.collidepoint(event.pos):
                    scale_mode = not scale_mode
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
            # Play audio when P is pressed
            elif event.key == pygame.K_p:
                local_height = (GRAPH_HEIGHT_UPPER - GRAPH_HEIGHT_LOWER)/2
                if draw_curve == 0:
                    audio.audio_from_function(line_func,  switch_point_to_graph((GRAPH_WIDTH_UPPER, local_height))[0]
                                              - switch_point_to_graph((GRAPH_WIDTH_LOWER, local_height))[0])
                else:
                    audio.audio_from_function(curve_func, switch_point_to_graph((GRAPH_WIDTH_UPPER, local_height))[0]
                                              - switch_point_to_graph((GRAPH_WIDTH_LOWER, local_height))[0])

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
        x_text = font.render(f"{round(switch_point_to_graph((x, line_start[1]))[0]/1000, 1)}", True, (0, 0, 0))
        screen.blit(x_text, (x + 1, line_start[1] + 5))
        pygame.draw.line(screen, AXIS_COLOR, (x, line_start[1]), (x, line_start[1] - 10), 3)
    if debug_mode:
        for y in range(GRAPH_HEIGHT_LOWER, GRAPH_HEIGHT_UPPER, GRID_SPACING):
            font = pygame.font.Font(None, 14)
            y_text = font.render(f"{switch_to_gui(switch_point_to_graph((line_start[0], y)))[1]}", True, (0, 0, 0))
            screen.blit(y_text, (line_start[0] - 20, y + 1))
            pygame.draw.line(screen, AXIS_COLOR, (line_start[0], y), (line_start[0] + 10, y), 3)
    else:
        for y in range(GRAPH_HEIGHT_LOWER, GRAPH_HEIGHT_UPPER+GRID_SPACING, GRID_SPACING):
            font = pygame.font.Font(None, 14)
            y_text = font.render(f"{round(switch_point_to_graph((line_start[0], y))[1], 2)}", True, (0, 0, 0))
            screen.blit(y_text, (line_start[0] - 20, y + 1))
            pygame.draw.line(screen, AXIS_COLOR, (line_start[0], y), (line_start[0] + 10, y), 3)

    # Draw the curve
    if draw_curve > 0:
        # If there's an update to the curve
        if is_moving_line or change_curve:
            graph_points = [switch_point_to_graph(point) for point in line_points]
            # Lagrange
            if draw_curve == 1:
                curve_func = lagrange.build_lagrange([graph_points[index][0] for index in range(len(graph_points))],
                                                  [graph_points[index][1] for index in range(len(graph_points))])
            # Spline
            elif draw_curve == 2:
                curve_func = scipy.interpolate.CubicSpline([graph_points[index][0] for index in range(len(graph_points))],
                                                  [graph_points[index][1] for index in range(len(graph_points))])
            points = [(switch_point_to_graph((x, 0))[0], curve_func(switch_point_to_graph((x, 0))[0]))
                      for x in np.linspace(GRAPH_WIDTH_LOWER, GRAPH_WIDTH_UPPER, 22000)]
            # Switch the curve points from graph points to gui points
            curve_points_gui = [switch_to_gui(point) for point in points]
            output_line = curve_points_gui
            print(points[:10])
            print(curve_points_gui[:10])
            print(f"Curve points gui len: {len(curve_points_gui)}")
        output_line = curve_points_gui
        # Scale mode
        if scale_mode:
            max_val = max(output_line, key=lambda coord: coord[1])[1]
            min_val = min(output_line, key=lambda coord: coord[1])[1]
            scale = 1
            half_height = (GRAPH_HEIGHT_UPPER - GRAPH_HEIGHT_LOWER) / 2 + GRAPH_HEIGHT_LOWER
            # if max_val - GRAPH_HEIGHT_UPPER > 0:
            #     scale = (max_val - half_height) / half_height
            # elif GRAPH_HEIGHT_LOWER - min_val > 0:
            #     scale = (half_height - min_val) / half_height
            ratio = 1
            if (max_val - min_val) > 0:
                ratio = (GRAPH_HEIGHT_UPPER - GRAPH_HEIGHT_LOWER) / (max_val - min_val)
            output_line = [
                (x, GRAPH_HEIGHT_LOWER + ratio * (y - min_val)) for (x, y)
                in output_line]
            graph_points = [switch_point_to_graph(point) for point in line_points]
        pygame.draw.aalines(screen, LINE_COLOR, False, output_line, LINE_THICKNESS)
    else:
        # Draw the line
        for index in range(len(line_points) - 1):
            pygame.draw.aaline(screen, LINE_COLOR, line_points[index], line_points[index + 1], LINE_THICKNESS)

    # Draw the points pressed:
    for point in line_points:
        pygame.draw.circle(screen, POINT_COLOR, point, 5)

    # Draw the UI box
    pygame.draw.rect(screen, UI_BOX_COLOR, ui_box)
    if draw_curve == 1:
        screen.blit(lagrange_text, (20, 20))
    elif draw_curve == 2:
        screen.blit(spline_text, (20, 20))
    else:
        screen.blit(line_text, (20, 20))

    # Draw the Debug box
    pygame.draw.rect(screen, UI_BOX_COLOR, debug_box)
    if debug_mode:
        screen.blit(debugging_text, (20, 80))
    else:
        screen.blit(debug_text, (20, 80))

    # Draw the Scale box
    pygame.draw.rect(screen, UI_BOX_COLOR, scale_box)
    if scale_mode:
        screen.blit(scaling_text, (20, 140))
    else:
        screen.blit(scale_text, (20, 140))

    # Render the cursor position
    screen.blit(position_text, (GRAPH_WIDTH_LOWER, HEIGHT - 40))

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()
