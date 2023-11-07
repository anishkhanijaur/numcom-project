import pygame
import sys
import math
import lagrange
import scipy

'''
    TODO: . Add the functionality to limit the number of constants in the fft approximation.
          . Figure out how to compile this code to become like an exe file.
          . How to save the produced sound.
          . H to show the help menu
          . Scale graph with button to decide
          . Hermite curve
'''

# Initialize Pygame
pygame.init()

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

# Line properties
line_start = [GRAPH_WIDTH_LOWER, int(HEIGHT / 2)]
line_end = [GRAPH_WIDTH_UPPER, int(HEIGHT / 2)]
line_points = [line_start, line_end]
curve_points = [line_start, line_end]
is_dragging_start = False
is_dragging_end = False
is_moving_line = False
draw_curve = 0
interpolation_methods = 2

# UI properties
ui_box = pygame.Rect(10, 10, 150, 40)
debug_box = pygame.Rect(10, 70, 150, 40)
font = pygame.font.Font(None, 30)
curve_text = font.render("Curve", True, (0, 0, 0))
lagrange_text = font.render("Lagrange", True, (0, 0, 0))
spline_text = font.render("Spline", True, (0, 0, 0))
line_text = font.render("Line", True, (0, 0, 0))
debug_text = font.render("Debug", True, (0, 0, 0))
debugging_text = font.render("Debugging", True, (0, 0, 0))


# Returns the y value of the line at the cursor's x position
def line_func(x: int) -> int:
    for index in range(len(line_points) - 1):
        if line_points[index][0] < x < line_points[index + 1][0]:
            x1, y1 = line_points[index]
            x2, y2 = line_points[index + 1]
            # calculate y = mx + c
            m = (y2 - y1) / (x2 - x1)
            c = y2 - m * x2
            return m * x + c
    print("The point does not exist in the line")
    return 0  # This would be rather unfortunate

def switch_point_to_graph(point: (int, int)) -> (int, int):
    x, y = point
    y = HEIGHT/2 - y
    return (x - GRAPH_WIDTH_LOWER, y)

def switch_to_gui(point: (int, int)) -> (int, int):
    x, y = point
    y = HEIGHT/2 - y
    return (x + GRAPH_WIDTH_LOWER, y)


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
debug_mode = False
change_curve = False
while running:
    change_curve = False
    screen.fill((255, 255, 255))  # Background color
    for event in pygame.event.get():
        # Update the position of the cursor when the cursor is within the bounds of the graph
        if event.type == pygame.MOUSEMOTION and within_graph_bounds(event.pos):
            font = pygame.font.Font(None, 25)
            position_text = font.render(f"x: {event.pos[0]}, y: {event.pos[1]}", True, (100, 0, 0))
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
                curve_points = [line_start, line_end]
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
        x_text = font.render(f"{x - GRAPH_WIDTH_LOWER}", True, (0, 0, 0))
        screen.blit(x_text, (x + 1, line_start[1] + 5))
        pygame.draw.line(screen, AXIS_COLOR, (x, line_start[1]), (x, line_start[1] - 10), 3)
    if debug_mode:
        for y in range(GRAPH_HEIGHT_LOWER, GRAPH_HEIGHT_UPPER, GRID_SPACING):
            font = pygame.font.Font(None, 14)
            y_text = font.render(f"{switch_to_gui(switch_point_to_graph((line_start[0], y)))[1]}", True, (0, 0, 0))
            screen.blit(y_text, (line_start[0] - 20, y + 1))
            pygame.draw.line(screen, AXIS_COLOR, (line_start[0], y), (line_start[0] + 10, y), 3)
    else:
        for y in range(GRAPH_HEIGHT_LOWER, GRAPH_HEIGHT_UPPER, GRID_SPACING):
            font = pygame.font.Font(None, 14)
            y_text = font.render(f"{switch_point_to_graph((line_start[0], y))[1]}", True, (0, 0, 0))
            screen.blit(y_text, (line_start[0] - 20, y + 1))
            pygame.draw.line(screen, AXIS_COLOR, (line_start[0], y), (line_start[0] + 10, y), 3)

    # Draw the line or curve
    if draw_curve == 1:
        # Lagrange
        if is_moving_line or change_curve:
            graph_points = [switch_point_to_graph(point) for point in line_points]
            lg_func = lagrange.build_lagrange([graph_points[index][0] for index in range(len(graph_points))],
                                              [graph_points[index][1] for index in range(len(graph_points))])
            curve_points = [switch_to_gui((x, int(lg_func(x)))) for x in range(graph_points[0][0], graph_points[-1][0])]
        pygame.draw.aalines(screen, LINE_COLOR, False, curve_points, LINE_THICKNESS)
    elif draw_curve == 2 or change_curve:
        # Spline
        if is_moving_line:
            graph_points = [switch_point_to_graph(point) for point in line_points]
            cs_func = scipy.interpolate.CubicSpline([graph_points[index][0] for index in range(len(graph_points))],
                                              [graph_points[index][1] for index in range(len(graph_points))])
            curve_points = [switch_to_gui((x, int(cs_func(x)))) for x in range(graph_points[0][0], graph_points[-1][0])]
        pygame.draw.aalines(screen, LINE_COLOR, False, curve_points, LINE_THICKNESS)
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

    # Render the cursor position
    screen.blit(position_text, (GRAPH_WIDTH_LOWER, HEIGHT - 40))

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()