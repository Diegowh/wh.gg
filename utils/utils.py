def get_game_type(queue_id):
    game_types = {
        400: "Normal Draft",
        420: "Ranked Solo",
        430: "Normal Blind",
        440: "Ranked Flex",
        450: "ARAM",
        700: "CLASH",
        830: "Co-op vs AI",
        840: "Co-op vs AI",
        850: "Co-op vs AI",
        900: "URF",
    }
    return game_types.get(queue_id, "Unknown")