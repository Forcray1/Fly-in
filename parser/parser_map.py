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


class ConnectionData(TypedDict):
    """
    Normalized representation of one connection line.
    """
    from_: str
    to: str
    max_link_capacity: int
    spec: dict[str, str]


class ParsedMap(TypedDict):
    """
    Complete parsed map payload.
    """

    nb_drones: int | None
    start_hub: HubData | None
    end_hub: HubData | None
    hubs: list[HubData]
    connections: list[ConnectionData]
    hub: list[HubData]


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
        if key.strip() in parsed:
            raise SpecError(f"Duplicate key in spec block: '{key.strip()}'")
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

    max_link_capacity = None
    if "max_link_capacity" in spec:
        try:
            max_link_capacity = int(spec["max_link_capacity"])
        except Exception:
            max_link_capacity = None
    nb_drones = None
    import inspect
    frame = inspect.currentframe()
    while frame:
        if "info" in frame.f_locals and "nb_drones" in frame.f_locals["info"]:
            nb_drones = frame.f_locals["info"]["nb_drones"]
            break
        frame = frame.f_back
    if nb_drones is not None:
        try:
            nb_drones = int(nb_drones)
        except Exception:
            nb_drones = 1
    if (
        max_link_capacity is None
        or (nb_drones is not None and max_link_capacity < nb_drones)
    ):
        max_link_capacity = nb_drones if nb_drones is not None else 1
        spec["max_link_capacity"] = str(max_link_capacity)
    return {
        "from_": zone_a,
        "to": zone_b,
        "max_link_capacity": max_link_capacity,
        "spec": spec,
    }


def parser(config: str) -> dict:
    """
    Parse one map file and return a dict.
    """

    map_path = Path(config)
    if not map_path.exists() or not map_path.is_file():
        raise FileNotFoundError(f"Map file not found: {config}")

    info: ParsedMap = {
        "nb_drones": None,
        "start_hub": None,
        "end_hub": None,
        "hubs": [],
        "connections": [],
        "hub": [],
    }

    with map_path.open("r", encoding="utf-8") as f:
        nb_drones_value = None
        lines = list(f)
        for line_no, raw_line in enumerate(lines, start=1):
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if ":" not in line:
                continue
            item, value = line.split(":", 1)
            item = item.strip()
            value = value.strip()
            if item == "nb_drones":
                try:
                    nb_drones_value = int(value)
                except ValueError as exc:
                    raise ValueError(
                        f"Line {line_no}: nb_drones must be an integer"
                    ) from exc
                if nb_drones_value <= 0:
                    raise ValueError(f"Line {line_no}: nb_drones must be > 0")
                info["nb_drones"] = nb_drones_value
        for line_no, raw_line in enumerate(lines, start=1):
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if ":" not in line:
                raise ValueError(f"Line {line_no}: missing ':' separator")
            item, value = line.split(":", 1)
            item = item.strip()
            value = value.strip()
            if item == "nb_drones":
                continue
            if item in {"start_hub", "hub", "end_hub"}:
                from typing import cast
                hub = _parse_hub(
                    value,
                    line_no,
                    cast(
                        Literal["start_hub", "hub", "end_hub"],
                        item
                    )
                )
                if item == "start_hub":
                    if info["start_hub"] is not None:
                        raise ValueError("Map contains multiple start_hub "
                                         "entries")
                    if nb_drones_value is not None and (
                        ("max_drones" not in hub["spec"])
                    ):
                        hub["max_drones"] = nb_drones_value
                        hub["spec"]["max_drones"] = str(nb_drones_value)
                    info["start_hub"] = hub
                    info["hub"].append(hub)
                    if (
                        nb_drones_value is not None
                        and hub["max_drones"] < nb_drones_value
                    ):
                        raise ValueError("Start hub doesn't have the capacity "
                                         "to handle all the drones")
                elif item == "end_hub":
                    if info["end_hub"] is not None:
                        raise ValueError("Map contains multiple end_hub "
                                         "entries")
                    if nb_drones_value is not None and (
                        ("max_drones" not in hub["spec"])
                    ):
                        hub["max_drones"] = nb_drones_value
                        hub["spec"]["max_drones"] = str(nb_drones_value)
                    info["end_hub"] = hub
                    info["hub"].append(hub)
                    if (
                        nb_drones_value is not None
                        and hub["max_drones"] < nb_drones_value
                    ):
                        raise ValueError("End hub doesn't have the capacity "
                                         "to handle all the drones")
                else:
                    info["hubs"].append(hub)
                    info["hub"].append(hub)
                continue

            if item == "connection":
                connection = _parse_connection(value, line_no)
                info["connections"].append(connection)
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
        if connection["from_"] not in known_zone_names:
            raise ValueError(
                f"Unknown zone in connection: {connection['from_']}"
            )
        if connection["to"] not in known_zone_names:
            raise ValueError(f"Unknown zone in connection: {connection['to']}")

    result = {k: v for k, v in info.items() if v is not None}
    return result
