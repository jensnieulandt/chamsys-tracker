import pygame
import socket

# Initialize pygame
pygame.init()

IS_DEBUG_ENABLED = False

# Screen settings
WIDTH, HEIGHT = 800, 600
LOGGER_WIDTH = 200  # Space for the logger panel
GRID_SPACING = 50  # Distance between grid lines
CIRCLE_SPACING = 75  # Distance between each concentric circle
screen = pygame.display.set_mode((WIDTH + LOGGER_WIDTH, HEIGHT))
pygame.display.set_caption("Crosshair Controller")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (50, 50, 50)
GRID_COLOR = (80, 80, 80)  # Slightly lighter gray for grid lines
CIRCLE_COLOR = (100, 100, 100)  # Slightly lighter gray for circle grid
TRACKER1_COLOR = (0, 0, 255)  # Blue for tracker 1
TRACKER2_COLOR = (255, 0, 0)  # Red for tracker 2

# Crosshair settings
tracker_1_pos = [WIDTH // 2, HEIGHT // 2]
tracker_2_pos = [WIDTH // 2, HEIGHT // 2]
CROSSHAIR_SIZE = 10
SPEED = 5
BOOST_SPEED = 10  # Speed boost when SHIFT or RT trigger is held
DEAD_ZONE = 0.1  # Threshold for ignoring small joystick movements
LAST_KEY = "None"  # To store last key pressed

# UDP settings
UDP_IP = "10.99.59.173"  # Set to the IP of ChamSys MagicQ
LOCAL_LISTENER_IP = socket.gethostbyname(socket.gethostname()) # Used for debugging
UDP_PORT = 6549  # Updated UDP port
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

if IS_DEBUG_ENABLED:
    udp_ip = UDP_IP
else:
    udp_ip = LOCAL_LISTENER_IP

# Initialize joystick
pygame.joystick.init()
if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()

# Font for logger
pygame.font.init()
font = pygame.font.Font(None, 24)

# Game loop
running = True
while running:
    screen.fill(BLACK)

    # Draw grid overlay
    for x in range(0, WIDTH, GRID_SPACING):
        pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, HEIGHT), 1)
    for y in range(0, HEIGHT, GRID_SPACING):
        pygame.draw.line(screen, GRID_COLOR, (0, y), (WIDTH, y), 1)

    # Draw concentric circles
    max_radius = min(WIDTH, HEIGHT) // 2  # Ensure circles fit within the screen
    center_x, center_y = WIDTH // 2, HEIGHT // 2
    for radius in range(CIRCLE_SPACING, max_radius, CIRCLE_SPACING):
        pygame.draw.circle(screen, CIRCLE_COLOR, (center_x, center_y), radius, 1)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.K_SPACE:
            tracker_1_pos = [WIDTH / 2, HEIGHT / 2]
        elif event.type == pygame.MOUSEMOTION:
            tracker_1_pos = list(event.pos)  # Update crosshair position with mouse
        elif event.type == pygame.KEYDOWN:
            LAST_KEY = pygame.key.name(event.key)  # Store the last key pressed
            if event.key == pygame.K_SPACE:
                tracker_1_pos = [WIDTH / 2, HEIGHT / 2]
                # console log
                print("Space key pressed, resetting crosshair position.")

    # Continuous movement when holding keys
    keys = pygame.key.get_pressed()
    current_speed_1 = BOOST_SPEED if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT] else SPEED
    current_speed_2 = SPEED

    # Joystick control with dead zone filtering
    if pygame.joystick.get_count() > 0:
        axis_x1 = joystick.get_axis(0)  # Left stick horizontal movement
        axis_y1 = joystick.get_axis(1)  # Left stick vertical movement
        axis_x2 = joystick.get_axis(2) # Right stick horizontal movement
        axis_y2 = joystick.get_axis(3)  # Right stick vertical movement
        left_trigger = joystick.get_axis(4)  # Left trigger (typically axis 4)
        rt_trigger = joystick.get_axis(5)  # Right trigger (typically axis 5)

        # Boost speed when RT is pressed (trigger values range from -1 to 1)
        if left_trigger > 0.1:
            current_speed_1 = BOOST_SPEED
        if rt_trigger > 0.1:
            current_speed_2 = BOOST_SPEED

        # Apply dead zone threshold
        if abs(axis_x1) > DEAD_ZONE:
            tracker_1_pos[0] += int(axis_x1 * current_speed_1 * 2)
        if abs(axis_y1) > DEAD_ZONE:
            tracker_1_pos[1] += int(axis_y1 * current_speed_1 * 2)
        if abs(axis_x2) > DEAD_ZONE:
            tracker_2_pos[0] += int(axis_x2 * current_speed_2 * 2)
        if abs(axis_y2) > DEAD_ZONE:
            tracker_2_pos[1] += int(axis_y2 * current_speed_2 * 2)

    # Keyboard movement
    if keys[pygame.K_LEFT]:
        tracker_1_pos[0] -= current_speed_1
    if keys[pygame.K_RIGHT]:
        tracker_1_pos[0] += current_speed_1
    if keys[pygame.K_UP]:
        tracker_1_pos[1] -= current_speed_1
    if keys[pygame.K_DOWN]:
        tracker_1_pos[1] += current_speed_1

    # Prevent the crosshair from leaving the screen
    tracker_1_pos[0] = max(CROSSHAIR_SIZE, min(WIDTH - (CROSSHAIR_SIZE/2), tracker_1_pos[0]))
    tracker_1_pos[1] = max(CROSSHAIR_SIZE, min(HEIGHT - (CROSSHAIR_SIZE/2), tracker_1_pos[1]))
    tracker_2_pos[0] = max(CROSSHAIR_SIZE, min(WIDTH - (CROSSHAIR_SIZE/2), tracker_2_pos[0]))
    tracker_2_pos[1] = max(CROSSHAIR_SIZE, min(HEIGHT - (CROSSHAIR_SIZE/2), tracker_2_pos[1]))

    # Send formatted position via UDP
    # Scale tracker_1_pos values between -6 and 6
    scaled_x1 = (tracker_1_pos[0] / WIDTH) * 20 - 10
    scaled_y1 = (tracker_1_pos[1] / HEIGHT) * 12 - 6
    position1_data = f"{scaled_x1:.0f},0,{scaled_y1:.0f},4,trackerName1"

    scaled_x2 = (tracker_2_pos[0] / WIDTH) * 20 - 10
    scaled_y2 = (tracker_2_pos[1] / HEIGHT) * 12 - 6
    position2_data = f"{scaled_x2:.0f},0,{scaled_y2:.0f},5,trackerName2"

    sock.sendto(position1_data.encode(), (udp_ip, UDP_PORT))
    sock.sendto(position2_data.encode(), (udp_ip, UDP_PORT))

    # Draw crosshair
    pygame.draw.line(screen, TRACKER1_COLOR, (tracker_1_pos[0] - CROSSHAIR_SIZE, tracker_1_pos[1]), 
                     (tracker_1_pos[0] + CROSSHAIR_SIZE, tracker_1_pos[1]), 2)
    pygame.draw.line(screen, TRACKER1_COLOR, (tracker_1_pos[0], tracker_1_pos[1] - CROSSHAIR_SIZE), 
                     (tracker_1_pos[0], tracker_1_pos[1] + CROSSHAIR_SIZE), 2)
    pygame.draw.line(screen, TRACKER2_COLOR, (tracker_2_pos[0] - CROSSHAIR_SIZE, tracker_2_pos[1]), 
                     (tracker_2_pos[0] + CROSSHAIR_SIZE, tracker_2_pos[1]), 2)
    pygame.draw.line(screen, TRACKER2_COLOR, (tracker_2_pos[0], tracker_2_pos[1] - CROSSHAIR_SIZE), 
                     (tracker_2_pos[0], tracker_2_pos[1] + CROSSHAIR_SIZE), 2)

    # Draw logger panel
    pygame.draw.rect(screen, GRAY, (WIDTH, 0, LOGGER_WIDTH, HEIGHT))  # Panel background
    logger_text = font.render(f"Blue: {position1_data}", True, WHITE)
    logger_text2 = font.render(f"Red: {position2_data}", True, WHITE)
    screen.blit(logger_text, (WIDTH + 10, 10))
    screen.blit(logger_text2, (WIDTH + 10, 30))

    # Display last key pressed
    last_key_text = font.render(f"Last Key: {LAST_KEY}", True, WHITE)
    screen.blit(last_key_text, (WIDTH + 10, 50))

    pygame.display.flip()
    pygame.time.delay(30)  # Adjust delay for smooth movement

pygame.quit()
