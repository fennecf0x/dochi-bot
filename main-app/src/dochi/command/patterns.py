def similar_character_pattern(char: str) -> str:
    if char == "뭐":
        return "(뭐|머|모)"
    if char == "뭘":
        return "(뭘|멀|몰)"
    if char == "줘":
        return "(줘|조|죠|줭|죵)"
    if char == "봐":
        return "(봐|바|봥|방)"
    if char == "게":
        return "(게|개|께)"
    if char == "했":
        return "(햇|햇)"
    return f"({char})"