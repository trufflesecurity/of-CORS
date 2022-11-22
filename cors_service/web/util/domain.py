def domain_to_all_subdomains(to_parse: str) -> list[str]:
    """Process the given domain into all domains and subdomains that it contains."""
    if to_parse == "":
        return []
    if to_parse.count(".") < 2:
        return [to_parse]
    to_return = []
    parts = to_parse.split(".")
    parts_reversed = list(reversed(parts))
    for i in range(len(parts_reversed) - 1):
        to_return.append(".".join(reversed(parts_reversed[: i + 2])))
    return to_return
