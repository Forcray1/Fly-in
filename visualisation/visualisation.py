import pygame

WIDTH, HEIGHT = 800, 600
ZONE_RADIUS = 25
DRONE_RADIUS = 10
FPS = 2

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)


def draw_graph(screen, graph):
    for zone_name, neighbors in graph.adjacency.items():
        zone = graph.zones[zone_name]
        for neighbor_name in neighbors:
            neighbor = graph.zones[neighbor_name]
            pygame.draw.line(
                screen, BLACK,
                (zone.x * 100 + 100, zone.y * 100 + 100),
                (neighbor.x * 100 + 100, neighbor.y * 100 + 100), 2)
    for zone in graph.zones.values():
        color = BLUE
        if hasattr(graph, 'start_hub') and zone.name == getattr(graph, 'start_hub', None).name:
            color = GREEN
        elif hasattr(graph, 'end_hub') and zone.name == getattr(graph, 'end_hub', None).name:
            color = RED
        elif hasattr(zone, 'zone_type') and zone.zone_type == 'priority':
            color = YELLOW
        pygame.draw.circle(
            screen, color,
            (zone.x * 100 + 100, zone.y * 100 + 100), ZONE_RADIUS)
        font = pygame.font.SysFont(None, 20)
        text = font.render(zone.name, True, BLACK)
        screen.blit(text, (zone.x * 100 + 80, zone.y * 100 + 80))


def draw_drones(screen, drones):
    from collections import defaultdict
    drones_by_zone = defaultdict(list)
    for drone in drones:
        drones_by_zone[drone.current_zone.name].append(drone)
    for zone_name, drones_list in drones_by_zone.items():
        base_x = drones_list[0].current_zone.x * 100 + 100
        base_y = drones_list[0].current_zone.y * 100 + 100
        for idx, drone in enumerate(drones_list):
            offset = (idx - (len(drones_list)-1)/2) * (DRONE_RADIUS*2+2)
            pygame.draw.circle(
                screen, BLACK,
                (int(base_x + offset), int(base_y)), DRONE_RADIUS)
            font = pygame.font.SysFont(None, 18)
            text = font.render(str(getattr(drone, 'drone_id', '?')), True, WHITE)
            screen.blit(text, (int(base_x + offset) - 7, int(base_y) - 7))


def visualise(graph, steps):
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Visualisation Graphe & Drones')
    clock = pygame.time.Clock()
    running = True
    step = 0
    while running and step < len(steps):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.fill(WHITE)
        draw_graph(screen, graph)
        draw_drones(screen, steps[step])
        pygame.display.flip()
        clock.tick(FPS)
        step += 1
    pygame.quit()
