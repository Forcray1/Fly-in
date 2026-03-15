def check_value(config: dict) -> bool:
    """
    Verify if each value parsed is correct
    """
    try:
        hub_names = [hub["name"] for hub in config["hub"]]
        for co in config["connections"]:
            if (
                co["from"] not in hub_names
                or co["to"] not in hub_names
            ):
                raise ValueError(f"{co} isn't a valid connection")
        seen_coords = set()
        for hub in config["hubs"]:
            coord = (hub["x"], hub["y"])
            if coord in seen_coords:
                raise ValueError(f"Duplicate hub coordinates "
                                 f"found: {coord}")
            seen_coords.add(coord)
        return True
    except ValueError as e:
        print(f"ERROR: {e}")
        return False
