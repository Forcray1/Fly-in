from pathlib import Path
from typing import Literal, TypedDict


class HubData(TypedDict):
    """
    Normalized representation of one hub line.
    """

    kind: Literal["start_hub", "hub", "end_hub"]
    name: str
    x: int
    y: int
    zone: str
    color: str
    max_drones: int
    spec: dict[str, str]


ConnectionData = TypedDict(
    "ConnectionData",
    {
        "from": str,
        "to": str,
        "max_link_capacity": int,
        "spec": dict[str, str],
    },
)


class ParsedMap(TypedDict):
    """
    Complete parsed map payload.
    """

    source: str
    nb_drones: int | None
    start_hub: HubData | None
    end_hub: HubData | None
    hubs: list[HubData]
    connections: list[ConnectionData]
    hub: list[HubData]
    connection: list[ConnectionData]


class CordError(ValueError):
    """
    Raised when hub coordinates are malformed.
    """
    pass


class SpecError(ValueError):
    """
    Raised when a [key=value ...] spec block is malformed.
    """
    pass


SUPPORTED_HUB_SPEC_KEYS: set[str] = {"color", "max_drones", "zone"}
SUPPORTED_CONNECTION_SPEC_KEYS: set[str] = {"max_link_capacity"}


def check_spec(specs: str) -> dict[str, str]:
    """
    Parse a spec block.
    """
    cleaned = specs.strip()
    if not cleaned:
        return {}

    if cleaned[0] == "[" and cleaned[-1] == "]":
        cleaned = cleaned[1:-1].strip()

    if not cleaned:
        return {}

    parsed: dict[str, str] = {}
    for token in cleaned.split():
        if "=" not in token:
            raise SpecError(f"Invalid token in spec block: {token}")
        key, value = token.split("=", 1)
        if not key or not value:
            raise SpecError(f"Invalid key/value in spec block: {token}")
        parsed[key.strip()] = value.strip()
    return parsed


def _split_main_and_spec(value: str) -> tuple[str, dict[str, str]]:
    """
    Split a directive payload into its main part and its optional spec.
    """

    value = value.strip()
    if "[" not in value:
        return value, {}

    open_bracket = value.find("[")
    close_bracket = value.rfind("]")
    if close_bracket < open_bracket:
        raise SpecError(f"Unclosed spec block: {value}")

    main = value[:open_bracket].strip()
    spec_block = value[open_bracket: close_bracket + 1]
    return main, check_spec(spec_block)


def _parse_hub(
    line_value: str,
    line_no: int,
    hub_type: Literal["start_hub", "hub", "end_hub"],
) -> HubData:
    """
    Parse one hub directive line value into a ``HubData`` dictionary.
    """

    main, spec = _split_main_and_spec(line_value)
    parts = main.split()
    if len(parts) != 3:
        raise CordError(f"Line {line_no}: expected '<name> <x> <y>', "
                        f"got: {main}")

    name, x_raw, y_raw = parts
    try:
        x = int(x_raw)
        y = int(y_raw)
    except ValueError as exc:
        raise CordError(f"Line {line_no}: coordinates must be "
                        f"integers") from exc

    for key in spec:
        if key not in SUPPORTED_HUB_SPEC_KEYS:
            raise SpecError(f"Line {line_no}: unsupported hub "
                            f"spec key '{key}'")

    max_drones = 1
    if "max_drones" in spec:
        try:
            max_drones = int(spec["max_drones"])
        except ValueError as exc:
            raise SpecError(f"Line {line_no}: max_drones must "
                            f"be an integer") from exc
        if max_drones <= 0:
            raise SpecError(f"Line {line_no}: max_drones must be > 0")

    return {
        "kind": hub_type,
        "name": name,
        "x": x,
        "y": y,
        "zone": spec.get("zone", "normal"),
        "color": spec.get("color", "none"),
        "max_drones": max_drones,
        "spec": spec,
    }


def _parse_connection(line_value: str, line_no: int) -> ConnectionData:
    """
    Parse one connection directive line value into ``ConnectionData``.
    """

    main, spec = _split_main_and_spec(line_value)
    if "-" not in main:
        raise ValueError(f"Line {line_no}: connection must be "
                         f"'<zone_a>-<zone_b>'")

    zone_a, zone_b = main.split("-", 1)
    zone_a = zone_a.strip()
    zone_b = zone_b.strip()
    if not zone_a or not zone_b:
        raise ValueError(f"Line {line_no}: invalid connection endpoints")

    for key in spec:
        if key not in SUPPORTED_CONNECTION_SPEC_KEYS:
            raise SpecError(f"Line {line_no}: unsupported connection "
                            f"spec key '{key}'")

    capacity = 1
    if "max_link_capacity" in spec:
        try:
            capacity = int(spec["max_link_capacity"])
        except ValueError as exc:
            raise SpecError(
                f"Line {line_no}: max_link_capacity must be an integer"
            ) from exc
        if capacity <= 0:
            raise SpecError(f"Line {line_no}: max_link_capacity must be > 0")

    return {
        "from": zone_a,
        "to": zone_b,
        "max_link_capacity": capacity,
        "spec": spec,
    }


def parser(config: str) -> ParsedMap:
    """
    Parse one map file and return a normalized structure.
    """

    map_path = Path(config)
    if not map_path.exists() or not map_path.is_file():
        raise FileNotFoundError(f"Map file not found: {config}")

    info: ParsedMap = {
        "source": str(map_path),
        "nb_drones": None,
        "start_hub": None,
        "end_hub": None,
        "hubs": [],
        "connections": [],
        "hub": [],
        "connection": [],
    }

    with map_path.open("r", encoding="utf-8") as f:
        for line_no, raw_line in enumerate(f, start=1):
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue

            if ":" not in line:
                raise ValueError(f"Line {line_no}: missing ':' separator")
            item, value = line.split(":", 1)
            item = item.strip()
            value = value.strip()

            if item == "nb_drones":
                try:
                    nb_drones = int(value)
                except ValueError as exc:
                    raise ValueError(
                        f"Line {line_no}: nb_drones must be an integer"
                    ) from exc
                if nb_drones <= 0:
                    raise ValueError(f"Line {line_no}: nb_drones must be > 0")
                info["nb_drones"] = nb_drones
                continue

            if item in {"start_hub", "hub", "end_hub"}:
                hub = _parse_hub(value, line_no, item)
                if item == "start_hub":
                    if info["start_hub"] is not None:
                        raise ValueError("Map contains multiple start_hub "
                                         "entries")
                    info["start_hub"] = hub
                elif item == "end_hub":
                    if info["end_hub"] is not None:
                        raise ValueError("Map contains multiple end_hub "
                                         "entries")
                    info["end_hub"] = hub
                else:
                    info["hubs"].append(hub)
                    info["hub"].append(hub)
                continue

            if item == "connection":
                connection = _parse_connection(value, line_no)
                info["connections"].append(connection)
                info["connection"].append(connection)
                continue

            raise ValueError(f"Line {line_no}: unsupported directive '{item}'")

    if info["nb_drones"] is None:
        raise ValueError("Map is missing 'nb_drones' entry")
    if info["start_hub"] is None:
        raise ValueError("Map is missing 'start_hub' entry")
    if info["end_hub"] is None:
        raise ValueError("Map is missing 'end_hub' entry")

    known_zone_names: set[str] = {hub["name"] for hub in info["hubs"]}
    known_zone_names.add(info["start_hub"]["name"])
    known_zone_names.add(info["end_hub"]["name"])
    for connection in info["connections"]:
        if connection["from"] not in known_zone_names:
            raise ValueError(
                f"Unknown zone in connection: {connection['from']}"
            )
        if connection["to"] not in known_zone_names:
            raise ValueError(f"Unknown zone in connection: {connection['to']}")

    return info
