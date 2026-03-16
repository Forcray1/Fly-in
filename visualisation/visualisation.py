import pygame
import time

WIDTH, HEIGHT = 1600, 1200
ZONE_RADIUS = 25
DRONE_RADIUS = 10
FPS = 2

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)


def get_graph_offset_scale(graph):
    xs = [zone.x for zone in graph.zones.values()]
    ys = [zone.y for zone in graph.zones.values()]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    graph_width = max_x - min_x if max_x > min_x else 1
    graph_height = max_y - min_y if max_y > min_y else 1
    margin = 80
    scale_x = (WIDTH - 2 * margin) / graph_width if graph_width else 1
    scale_y = (HEIGHT - 2 * margin) / graph_height if graph_height else 1
    scale = min(scale_x, scale_y, 200)
    center_x = (min_x + max_x) / 2
    center_y = (min_y + max_y) / 2
    screen_cx = WIDTH // 2
    screen_cy = HEIGHT // 2
    return scale, center_x, center_y, screen_cx, screen_cy


def to_screen_coords(x, y, scale, center_x, center_y, screen_cx, screen_cy):
    sx = int((x - center_x) * scale + screen_cx)
    sy = int((y - center_y) * scale + screen_cy)
    return sx, sy


def draw_graph(screen, graph):
    (scale, center_x, center_y,
     screen_cx, screen_cy) = get_graph_offset_scale(graph)
    for zone_name, neighbors in graph.adjacency.items():
        zone = graph.zones[zone_name]
        for neighbor_name in neighbors:
            neighbor = graph.zones[neighbor_name]
            start = to_screen_coords(
                zone.x, zone.y, scale, center_x, center_y, screen_cx, screen_cy
            )
            end = to_screen_coords(
                neighbor.x, neighbor.y, scale, center_x, center_y,
                screen_cx, screen_cy
            )
            pygame.draw.line(screen, BLACK, start, end, 2)
    for zone in graph.zones.values():
        color = BLUE
        start_hub = getattr(graph, 'start_hub', None)
        end_hub = getattr(graph, 'end_hub', None)
        if start_hub is not None and zone.name == start_hub.name:
            color = GREEN
        elif end_hub is not None and zone.name == end_hub.name:
            color = RED
        elif hasattr(zone, 'zone_type') and zone.zone_type == 'priority':
            color = YELLOW
        pos = to_screen_coords(
            zone.x, zone.y, scale, center_x, center_y, screen_cx, screen_cy
        )
        pygame.draw.circle(screen, color, pos, ZONE_RADIUS)
        font = pygame.font.SysFont(None, 20)
        text = font.render(zone.name, True, BLACK)
        screen.blit(text, (pos[0] - ZONE_RADIUS, pos[1] - ZONE_RADIUS))


def draw_drones(screen, drones, graph):
    from collections import defaultdict
    if not drones:
        return
    scale, center_x, center_y, screen_cx, screen_cy = get_graph_offset_scale(
        graph
    )
    drones_by_zone = defaultdict(list)
    for drone in drones:
        drones_by_zone[drone.current_zone.name].append(drone)
    for zone_name, drones_list in drones_by_zone.items():
        base_x, base_y = to_screen_coords(
            drones_list[0].current_zone.x,
            drones_list[0].current_zone.y,
            scale, center_x, center_y, screen_cx, screen_cy)
        for idx, drone in enumerate(drones_list):
            offset = (idx - (len(drones_list)-1)/2) * (DRONE_RADIUS*2+2)
            pygame.draw.circle(
                screen, BLACK,
                (int(base_x + offset), int(base_y)), DRONE_RADIUS)
            font = pygame.font.SysFont(None, 18)
            text = font.render(str(getattr(drone,
                                           'drone_id',
                                           '?')), True, WHITE)
            screen.blit(text, (int(base_x + offset) - 7, int(base_y) - 7))


def visualise(graph, steps):
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Visualisation Graphe & Drones')
    clock = pygame.time.Clock()
    running = True
    step = 0
    if len(steps) == 0:
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            screen.fill(WHITE)
            draw_graph(screen, graph)
            pygame.display.flip()
            clock.tick(50)
        pygame.quit()
        return
    while running and step < len(steps):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.fill(WHITE)
        draw_graph(screen, graph)
        draw_drones(screen, steps[step], graph)
        pygame.display.flip()
        clock.tick(100)
        time.sleep(1)
        step += 1
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        if len(steps) > 0:
            screen.fill(WHITE)
            draw_graph(screen, graph)
            draw_drones(screen, steps[-1], graph)
            pygame.display.flip()
        clock.tick(50)
    pygame.quit()
