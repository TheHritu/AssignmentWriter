from typing import NamedTuple


class Layout(NamedTuple):
    max_line_length: int
    margin_left: int
    margin_top: int
    font_size: int
    line_spacing: float
    margin_bottom: int


COLORED = ("cream", "cyan", "lightblue", "lightgreen", "lime", "orange", "pink")

_A4 = {
    "adinekirnberg": (76, 20, 20, 40, 10),
    "alanishand": (54, 20, 20, 35, 13),
    "architex": (46, 20, 20, 43, 13),
    "caveat": (43, 20, 20, 40, 10),
    "greatvibesregular": (62, 20, 20, 30, 10),
    "hand_note": (56, 20, 20, 40, 12),
    "homemadeapple": (42, 20, 20, 25, 6),
    "honeyscript": (56, 20, 20, 45, 13),
    "jottflf": (43, 20, 20, 35, 12),
    "note_this": (49, 20, 20, 30, 12),
    "pleasewritemeasong": (52, 20, 20, 35, 13),
    "s_hand": (43, 20, 20, 50, 13),
}

_LINED = {
    "adinekirnberg": (60, 370, 330, 115, 2),
    "alanishand": (60, 370, 338, 80, 50),
    "architex": (63, 370, 348, 80, 22),
    "caveat": (52, 370, 333, 85, 22),
    "greatvibesregular": (60, 370, 340, 75, 15.5),
    "hand_note": (67, 370, 338, 85, 2.3),
    "homemadeapple": (45, 370, 310, 60, -1),
    "honeyscript": (83, 370, 338, 80, 9.5),
    "jottflf": (50, 370, 340, 75, 22.5),
    "note_this": (42, 370, 338, 85, 4),
    "pleasewritemeasong": (60, 370, 340, 75, 29.3),
    "s_hand": (55, 370, 323, 100, 41),
}

_ROUGH = {
    "adinekirnberg": (67, 155, 125, 45, 2),
    "alanishand": (63, 155, 135, 30, 19),
    "architex": (64, 155, 135, 35, 6),
    "caveat": (61, 155, 132, 30, 11),
    "greatvibesregular": (68, 150, 135, 30, 5),
    "hand_note": (80, 155, 135, 30, 4),
    "homemadeapple": (74, 155, 138, 15, 13),
    "honeyscript": (88, 155, 126, 32, 3.3),
    "jottflf": (60, 155, 138, 25, 13),
    "note_this": (75, 155, 143, 20, 16),
    "pleasewritemeasong": (73, 155, 138, 25, 16),
    "s_hand": (58, 155, 132, 40, 15.8),
}

_SPIRAL = {
    "adinekirnberg": (65, 440, 407, 115, -12),
    "alanishand": (66, 440, 422, 70, 41.5),
    "architex": (78, 440, 432, 70, 18),
    "caveat": (64, 440, 417, 75, 17),
    "greatvibesregular": (71, 440, 417, 75, 1.5),
    "hand_note": (76, 440, 422, 75, -0.2),
    "homemadeapple": (47, 440, 410, 60, -16.8),
    "honeyscript": (98, 440, 422, 70, 5.5),
    "jottflf": (56, 440, 417, 75, 7.9),
    "note_this": (53, 440, 422, 75, 1),
    "pleasewritemeasong": (66, 440, 417, 75, 14.7),
    "s_hand": (67, 440, 407, 90, 32),
}

_WRINKLED = {
    "adinekirnberg": (55, 140, 62, 71, -8),
    "alanishand": (64, 140, 77, 35, 29.5),
    "architex": (72, 140, 87, 35, 18),
    "caveat": (58, 140, 62, 40, 14),
    "greatvibesregular": (65, 140, 77, 37, 10.5),
    "hand_note": (73, 140, 77, 40, 4.8),
    "homemadeapple": (54, 140, 70, 25, 9.2),
    "honeyscript": (92, 140, 77, 35, 12.5),
    "jottflf": (48, 140, 77, 38, 11.9),
    "note_this": (47, 140, 67, 40, 7),
    "pleasewritemeasong": (58, 140, 77, 38, 15.7),
    "s_hand": (54, 140, 72, 50, 22),
}

_COLORED = {
    "adinekirnberg": (62, 250, 60, 50, 10),
    "alanishand": (53, 250, 60, 45, 13),
    "architex": (45, 250, 60, 53, 13),
    "caveat": (42, 250, 60, 50, 10),
    "greatvibesregular": (76, 250, 60, 30, 10),
    "hand_note": (55, 250, 60, 50, 12),
    "homemadeapple": (36, 250, 60, 35, 6),
    "honeyscript": (55, 250, 60, 55, 13),
    "jottflf": (42, 250, 60, 45, 12),
    "note_this": (43, 250, 60, 40, 12),
    "pleasewritemeasong": (51, 250, 60, 45, 13),
    "s_hand": (42, 250, 60, 60, 13),
}


def _layouts(rows: dict, margin_bottom: int) -> dict:
    return {font: Layout(*row, margin_bottom) for font, row in rows.items()}


LAYOUTS = {
    "a4": _layouts(_A4, 20),
    "lined": _layouts(_LINED, 130),
    "rough": _layouts(_ROUGH, 130),
    "spiral": _layouts(_SPIRAL, 130),
    "wrinkled": _layouts(_WRINKLED, 50),
}

for _name in COLORED:
    LAYOUTS[_name] = _layouts(_COLORED, 50)
