import pygame
import time
import math
from collections import defaultdict
from typing import Dict, List, Tuple, Any

WIDTH: int = 1600
HEIGHT: int = 1000
DRONE_RADIUS: int = 8

DEFAULT_COLORS: Dict[str, Tuple[int, int, int]] = {
    "start": (46, 204, 113),
    "end": (231, 76, 60),
    "restricted": (149, 165, 166),
    "priority": (241, 196, 15),
    "normal": (100, 100, 250),
    "background": (245, 245, 245),
    "edge": (180, 180, 180),
    "shadow": (50, 50, 50),
    "text_bg": (255, 255, 255)
}

COLOR_MAP: Dict[str, Tuple[int, int, int]] = {
    "red": (231, 76, 60),
    "green": (46, 204, 113),
    "blue": (52, 152, 219),
    "yellow": (241, 196, 15),
    "gray": (149, 165, 166),
    "cyan": (0, 255, 255),
    "grey": (149, 165, 166),
    "purple": (155, 89, 182),
    "lime": (50, 205, 50),
    "magenta": (255, 0, 255),
    "brown": (139, 69, 19),
    "orange": (230, 126, 34),
    "white": (255, 255, 255),
    "black": (44, 62, 80),
    "brown": (139, 69, 19),
    "maroon": (128, 0, 0),
    "darkred": (139, 0, 0),
    "violet": (238, 130, 238),
    "crimson": (220, 20, 60),
    "rainbow": (100, 200, 255)
}


def get_zone_color(zone: Any, graph: Any) -> Tuple[int, int, int]:
    """
    Determine the color of a zone based on metadata or default type.
    """
    parsed_color: str = getattr(zone, 'color', 'none')
    if parsed_color in COLOR_MAP:
        return COLOR_MAP[parsed_color]

    if zone.name == graph.start_hub.name:
        return DEFAULT_COLORS["start"]
    if zone.name == graph.end_hub.name:
        return DEFAULT_COLORS["end"]

    z_type: str = getattr(zone, 'zone_type', 'normal')
    return DEFAULT_COLORS.get(z_type, DEFAULT_COLORS["normal"])


def get_dynamic_settings(graph: Any) -> Tuple[int, int]:
    """
    Calculate radius and font size based on the number of zones.
    """
    num_zones: int = len(graph.zones)
    if num_zones < 10:
        return 35, 24
    if num_zones < 30:
        return 25, 18
    return 15, 14


def get_graph_offset_scale(
    graph: Any, zone_radius: int
) -> Tuple[float, float, float, int, int]:
    """
    Compute scale and offset to fit the graph in the window.
    """
    xs: List[float] = [float(zone.x) for zone in graph.zones.values()]
    ys: List[float] = [float(zone.y) for zone in graph.zones.values()]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    graph_w: float = max_x - min_x if max_x > min_x else 1.0
    graph_h: float = max_y - min_y if max_y > min_y else 1.0

    margin: int = zone_radius * 4
    scale_x: float = (WIDTH - 2 * margin) / graph_w
    scale_y: float = (HEIGHT - 2 * margin) / graph_h
    scale: float = min(scale_x, scale_y)

    cx: float = (min_x + max_x) / 2
    cy: float = (min_y + max_y) / 2
    return scale, cx, cy, WIDTH // 2, HEIGHT // 2


def to_screen_coords(
    x: float, y: float, scale: float, cx: float, cy: float, scx: int, scy: int
) -> Tuple[int, int]:
    """
    Convert graph coordinates to screen coordinates.
    """
    return int((x - cx) * scale + scx), int((y - cy) * scale + scy)


def draw_graph(
    screen: pygame.Surface, graph: Any, zone_radius: int, font_size: int
) -> None:
    """
    Draw edges and zones using parsed or default colors.
    """
    scale, cx, cy, scx, scy = get_graph_offset_scale(graph, zone_radius)
    font = pygame.font.SysFont("Arial", font_size, bold=True)

    # Draw Connections
    for zone_name, neighbors in graph.adjacency.items():
        z1 = graph.zones[zone_name]
        p1 = to_screen_coords(z1.x, z1.y, scale, cx, cy, scx, scy)
        for n_name in neighbors:
            z2 = graph.zones[n_name]
            p2 = to_screen_coords(z2.x, z2.y, scale, cx, cy, scx, scy)
            pygame.draw.line(screen, DEFAULT_COLORS["edge"], p1, p2, 1)

    # Draw Zones
    for zone in graph.zones.values():
        pos = to_screen_coords(zone.x, zone.y, scale, cx, cy, scx, scy)
        color = get_zone_color(zone, graph)

        pygame.draw.circle(
            screen, DEFAULT_COLORS["shadow"], (pos[0] + 2, pos[1] + 2),
            zone_radius
        )
        pygame.draw.circle(screen, color, pos, zone_radius)

        # Label
        txt = font.render(zone.name, True, (0, 0, 0))
        txt_rect = txt.get_rect(center=(pos[0], pos[1] + zone_radius + 12))
        bg_rect = txt_rect.inflate(4, 2)
        pygame.draw.rect(screen, (255, 255, 255, 180), bg_rect)
        screen.blit(txt, txt_rect)


def draw_drones(
    screen: pygame.Surface, drones: List[Any], graph: Any, zone_radius: int
) -> None:
    """
    Draw drones with layout logic for multiple drones in one zone.
    """
    scale, cx, cy, scx, scy = get_graph_offset_scale(graph, zone_radius)
    d_by_z: Dict[str, List[Any]] = defaultdict(list)

    for drone in drones:
        transit_to = getattr(drone, 'in_transit_to', None)
        turns = getattr(drone, 'turns_to_arrival', 0)
        if turns > 0 and transit_to is not None:
            z_name: str = transit_to
        else:
            z_name = drone.current_zone.name
        d_by_z[z_name].append(drone)

    for zone_name, drones_list in d_by_z.items():
        if zone_name not in graph.zones:
            continue
        z = graph.zones[zone_name]
        bx, by = to_screen_coords(z.x, z.y, scale, cx, cy, scx, scy)

        num: int = len(drones_list)
        for idx, drone in enumerate(drones_list):
            dx, dy = bx, by
            if num > 1:
                angle: float = (2 * math.pi * idx) / num
                dist: float = zone_radius * 0.7
                dx = bx + int(dist * math.cos(angle))
                dy = by + int(dist * math.sin(angle))

            turns = getattr(drone, 'turns_to_arrival', 0)
            color: Tuple[int, int, int] = (255, 200, 0) if turns > 0 \
                else (255, 255, 255)

            pygame.draw.circle(screen, (0, 0, 0), (dx, dy), DRONE_RADIUS + 1)
            pygame.draw.circle(screen, color, (dx, dy), DRONE_RADIUS)

            f = pygame.font.SysFont(None, 16)
            t = f.render(str(drone.drone_id), True, (0, 0, 0))
            screen.blit(t, (dx - 5, dy - 5))


def visualise(graph: Any, steps: List[List[Any]]) -> None:
    """
    Main visualization loop for the simulation.
    """
    pygame.init()
    screen: pygame.Surface = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(f"Fly-in Sim - {len(graph.zones)} Zones")
    clock: pygame.time.Clock = pygame.time.Clock()

    zone_radius, font_size = get_dynamic_settings(graph)
    step: int = 0
    paused: bool = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                paused = not paused

        screen.fill(DEFAULT_COLORS["background"])
        idx: int = min(step, len(steps) - 1) if steps else 0

        draw_graph(screen, graph, zone_radius, font_size)
        if steps:
            draw_drones(screen, steps[idx], graph, zone_radius)

        # UI
        font_ui = pygame.font.SysFont("Arial", 30, bold=True)
        status: str = "(PAUSED)" if paused else ""
        ui_txt = font_ui.render(f"TURN: {idx} {status}", True, (50, 50, 50))
        screen.blit(ui_txt, (20, 20))

        pygame.display.flip()

        if not paused and step < len(steps):
            step += 1
            time.sleep(0.4)

        clock.tick(30)
