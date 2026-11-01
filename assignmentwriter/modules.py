import os
import re
import logging
import operator
import textwrap
from pathlib import Path
from dataclasses import dataclass
from PIL import Image, ImageDraw, ImageFont
from .layouts import COLORED, LAYOUTS, Layout

logger = logging.getLogger(__name__)

RES_DIR = Path(__file__).resolve().parent / "res"
PAPERS_DIR = RES_DIR / "papers"
FONTS_DIR = RES_DIR / "fonts"

DEFAULT_FILENAME = "assignment.png"
DEFAULT_PDF_FILENAME = "assignment.pdf"

PDF_PAGE_WIDTH_INCHES = 8.27

PAPERS = {
    "a4": "a4paper.jpg",
    "lined": "lined.png",
    "rough": "rough.jpg",
    "spiral": "spiral.png",
    "wrinkled": "wrinkled.jpg",
    **{name: f"{name}.jpg" for name in COLORED},
}

# In order, coz i used it in other projects.

FONTS = {
    "adinekirnberg": "AdineKirnberg.ttf",
    "alanishand": "AlanisHand.ttf",
    "architex": "Architex.ttf",
    "caveat": "caveat.ttf",
    "greatvibesregular": "GreatVibes-Regular.ttf",
    "hand_note": "Hand_Note.otf",
    "homemadeapple": "HomemadeApple.ttf",
    "honeyscript": "HoneyScript.ttf",
    "jottflf": "JottFLF.ttf",
    "note_this": "Note_this.ttf",
    "pleasewritemeasong": "pleasewritemeasong.ttf",
    "s_hand": "S_Hand.ttf",
}

FONT_ALIASES = {
    "greatvibes": "greatvibesregular",
}

INKS = {
    "blue": (19, 19, 148),
    "black": (19, 19, 20),
    "red": (163, 2, 2),
    "green": (0, 122, 0),
    "pencil": (105, 105, 105),
    "brown": (101, 67, 33),
    "purple": (75, 0, 130),
    "orange": (255, 140, 0),
    "teal": (0, 128, 128),
    "magenta": (139, 0, 139),
}


def _normalize(value) -> str:
    """Lower-case a name and drop everything that is not a letter or digit."""
    return re.sub(r"[^a-z0-9]", "", str(value).lower())


def available_papers() -> list:
    return [name for name, file in PAPERS.items() if (PAPERS_DIR / file).is_file()]


def available_fonts() -> list:
    return [name for name, file in FONTS.items() if (FONTS_DIR / file).is_file()]


def resolve_paper(value) -> str:
    """Return the paper name for `value` (case and spaces are ignored) or raise ValueError."""
    lookup = {_normalize(name): name for name in PAPERS}
    name = lookup.get(_normalize(value))
    if name is None:
        raise ValueError(f"Unknown Paper {value!r}. Choose one of: {', '.join(PAPERS)}")
    if name not in available_papers():
        raise ValueError(f"The image file for Paper {name!r} is missing")
    return name


def resolve_font(value) -> str:
    """Return the font name for `value` (spaces, dashes and case are ignored) or raise ValueError."""
    names = list(FONTS)
    text = str(value).strip()
    if re.fullmatch(r"\d+", text):
        number = int(text)
        if not 1 <= number <= len(names):
            raise ValueError(
                f"Unknown Font number {value!r}. Choose a number from 1 to {len(names)}"
            )
        name = names[number - 1]
    else:
        lookup = {_normalize(item): item for item in names}
        lookup.update(FONT_ALIASES)
        name = lookup.get(_normalize(text))
        if name is None:
            raise ValueError(
                f"Unknown Font {value!r}. Choose one of: {', '.join(names)}"
            )
    if name not in available_fonts():
        raise ValueError(f"The font file for Font {name!r} is missing")
    return name


def resolve_ink(value) -> str:
    """Return an ink name (e.g. "blue") or a hex colour like "1A2B3C".

    Raises ValueError if `value` is neither.
    """
    key = str(value).strip().lower()
    if key in INKS:
        return key
    code = key.removeprefix("#")
    if re.fullmatch(r"[0-9a-f]{6}", code):
        return code.upper()
    raise ValueError(
        f"Unknown Ink {value!r}. Choose one of: {', '.join(INKS)} "
        "or a 6-digit hex colour such as 131394"
    )


def ink_to_rgb(ink: str) -> tuple:
    """Turn a resolved ink (see `resolve_ink`) into an (R, G, B) tuple."""
    if ink in INKS:
        return INKS[ink]
    return (int(ink[0:2], 16), int(ink[2:4], 16), int(ink[4:6], 16))


def _pick(value, default):
    """Default picker LOL, L Hypergamy NGL."""
    return default if value is None else value


def _resolve_target(path, default_name: str, default_suffix: str) -> Path:
    """Turn what the user passed to save() into the file to write."""
    raw = os.fsdecode(path) if path is not None else default_name
    target = Path(raw)
    if target.is_dir() or raw.endswith(("/", os.sep)):
        return target / default_name
    if not target.suffix:
        return target.with_suffix(default_suffix)
    return target


def read_text_file(path) -> str:
    """Return the text of a UTF-8 text file (a BOM at the start is ignored).

    Raises ValueError, with a message that names the file, if it cannot be read.
    """
    if not isinstance(path, (str, os.PathLike)):
        raise ValueError("File must be the path of a text file, as a string or a Path")
    try:
        return Path(path).expanduser().read_text(encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError) as error:
        raise ValueError(f"Could not read {os.fspath(path)}: {error}") from error


@dataclass
class AssignmentConfigOptions:
    """Settings for the handwritten pages.

    Give either Text or File, not both. FontSize to LineSpacing are None by default.
    """

    Text: str | None = None
    Paper: str = "a4"
    Font: str = "caveat"
    Ink: str = "blue"
    KeepLineBreaks: bool = False
    FontSize: int | None = None
    MaxLineLength: int | None = None
    MarginLeft: int | None = None
    MarginTop: int | None = None
    MarginBottom: int | None = None
    LineSpacing: float | None = None
    File: str | os.PathLike | None = None

    def __post_init__(self):
        if self.File is not None:
            if self.Text is not None:
                raise ValueError("Give Text or File, not both")
            self.Text = read_text_file(self.File)

        if not isinstance(self.Text, str) or not self.Text.strip():
            raise ValueError("Nothing to write, Text (or File) is missing or empty")

        self.Ink = resolve_ink(self.Ink)
        self.Font = resolve_font(self.Font)
        self.Paper = resolve_paper(self.Paper)

        for name in ("FontSize", "MaxLineLength"):
            value = getattr(self, name)
            if value is not None and value < 1:
                raise ValueError(f"{name} must be at least 1")

        for name in ("MarginLeft", "MarginTop", "MarginBottom"):
            value = getattr(self, name)
            if value is not None and value < 0:
                raise ValueError(f"{name} can't be negative")

        # LineSpacing isn't checked here, _prepare() already complains if the lines would end up on top of each other


class AssignmentResult:
    """What `Assignment.create()` returns.

    - `bool(result)` is False if the pages could not be created.
    - `len(result)` is the number of pages, `result[0]` is the first page. Each page is a Pillow image that is drawn when you ask for it, so a long text does not keep every page in memory.
    - `result.image` is the first page.
    - `result.paths` are the files written by the last `save()` or `save_pdf()`, and `str(result)` is those paths, one per line (an empty string until something has been saved).
    """

    def __init__(self, render=None, page_count=0, config=None):
        self._render = render
        self.page_count = page_count
        self.config = config
        self.paths = []

    def __bool__(self) -> bool:
        return self.page_count > 0

    def __len__(self) -> int:
        return self.page_count

    def __getitem__(self, index):
        index = operator.index(index)
        if not -self.page_count <= index < self.page_count:
            raise IndexError("page index out of range")
        return self._render(index % self.page_count)

    def __iter__(self):
        return (self[index] for index in range(self.page_count))

    def __str__(self) -> str:
        return "\n".join(self.paths)

    def __repr__(self) -> str:
        if not self:
            return "<AssignmentResult failed>"
        pages = "page" if self.page_count == 1 else "pages"
        saved = f" saved={self.paths!r}" if self.paths else ""
        return f"<AssignmentResult {self.page_count} {pages}{saved}>"

    @property
    def image(self):
        """The first page as a Pillow image, or None if nothing was created."""
        return self[0] if self else None

    @property
    def pages(self):
        """Iterator over every page as a Pillow image."""
        return iter(self)

    def save(self, path=None, **kwargs):
        """Save every page and return the list of paths, or None if it failed.

        - `path` can be a file name or a folder; it defaults to `assignment.png` in the current folder.
        - When the text needs more than one page they are saved as `name_1.png`, `name_2.png` and so on.
        - Extra keyword arguments go to Pillow's `Image.save`.
        """
        if not self:
            logger.error("Nothing to save: the assignment pages were not created")
            return None

        target = _resolve_target(path, DEFAULT_FILENAME, ".png")
        if target.suffix.lower() in (".jpg", ".jpeg"):
            kwargs.setdefault(
                "quality", 95
            )  # Punish the guy for using JPEG when PNG exists. (MAYBE CHANGE IT TO 50 IN FUTURE)

        if self.page_count == 1:
            targets = [target]
        else:
            digits = len(str(self.page_count))
            targets = [
                target.with_name(f"{target.stem}_{number:0{digits}d}{target.suffix}")
                for number in range(1, self.page_count + 1)
            ]

        saved = []
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            for page_path, page in zip(targets, self):
                page.save(page_path, **kwargs)
                saved.append(os.fspath(page_path))
        except Exception as error:
            logger.error("Could not save the assignment pages to %s: %s", target, error)
            return None

        self.paths = saved
        return saved

    def save_pdf(self, path=None):
        """Save all pages as one PDF and return its path, or None if it failed.

        - `path` can be a file name or a folder; it defaults to `assignment.pdf` in the current folder
        - The pages are scaled to the width of an A4 sheet. All pages are kept in memory while the PDF is written.
        """
        if not self:
            logger.error("Nothing to save: the assignment pages were not created")
            return None

        target = _resolve_target(path, DEFAULT_PDF_FILENAME, ".pdf")
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            pages = list(self)
            pages[0].save(
                target,
                format="PDF",
                save_all=True,
                append_images=pages[1:],
                resolution=pages[0].width / PDF_PAGE_WIDTH_INCHES,
            )
        except Exception as error:
            logger.error("Could not save the assignment PDF to %s: %s", target, error)
            return None

        self.paths = [os.fspath(target)]
        return self.paths[0]


class Assignment:
    """Writes text on a paper in a handwriting font and ink.

    - Example:
        config = AssignmentConfigOptions(Text="Hello World", Paper="lined")
        result = Assignment(config).create()
        result.save("page.png")
    """

    def __init__(self, config: AssignmentConfigOptions):
        if not isinstance(config, AssignmentConfigOptions):
            raise TypeError("config must be an AssignmentConfigOptions instance")
        self.config = config

    def get_defaults(self) -> dict:
        layout = LAYOUTS[self.config.Paper][self.config.Font]
        return {
            "Paper": self.config.Paper,
            "Font": self.config.Font,
            "FontFile": FONTS[self.config.Font],
            "FontSize": layout.font_size,
            "MaxLineLength": layout.max_line_length,
            "MarginLeft": layout.margin_left,
            "MarginTop": layout.margin_top,
            "MarginBottom": layout.margin_bottom,
            "LineSpacing": layout.line_spacing,
        }

    def create(self) -> AssignmentResult:
        """Lay out the text. Returns a falsy AssignmentResult if anything fails."""
        try:
            render, page_count = self._prepare()
        except Exception as error:
            logger.error("Could not create the assignment pages: %s", error)
            return AssignmentResult()
        return AssignmentResult(render, page_count, self.config)

    def _layout(self) -> Layout:
        """The tuned layout with the config's overrides applied."""
        config = self.config
        layout = LAYOUTS[config.Paper][config.Font]
        return Layout(
            max_line_length=_pick(config.MaxLineLength, layout.max_line_length),
            margin_left=_pick(config.MarginLeft, layout.margin_left),
            margin_top=_pick(config.MarginTop, layout.margin_top),
            font_size=_pick(config.FontSize, layout.font_size),
            line_spacing=_pick(config.LineSpacing, layout.line_spacing),
            margin_bottom=_pick(config.MarginBottom, layout.margin_bottom),
        )

    def _wrap(self, width: int) -> list:
        """Break the text into lines of at most `width` characters."""
        text = self.config.Text
        if not self.config.KeepLineBreaks:
            return textwrap.wrap(text, width=width)

        lines = []
        for line in text.splitlines():
            lines.extend(textwrap.wrap(line, width=width) or [""])
        # blank lines at the very end would only add an empty page
        while lines and not lines[-1]:
            lines.pop()
        return lines

    def _prepare(self):
        """Work out the pages. Returns (render, page_count).

        `render(index)` draws page `index` (counting from 0) and returns it btw.
        """
        config = self.config
        layout = self._layout()

        with Image.open(PAPERS_DIR / PAPERS[config.Paper]) as paper:
            base = paper.convert("RGB")

        font = ImageFont.truetype(str(FONTS_DIR / FONTS[config.Font]), layout.font_size)
        color = ink_to_rgb(config.Ink)

        lines = self._wrap(layout.max_line_length)
        left, top, right, bottom = font.getbbox("Ay")
        line_height = (bottom - top) + layout.line_spacing
        if line_height <= 0:
            raise ValueError("LineSpacing is too small, the lines would overlap")
        available_height = base.height - layout.margin_top - layout.margin_bottom
        lines_per_page = int(available_height // line_height)
        if lines_per_page < 1:
            logger.warning(
                "Not even one line fits on the %s page, use a smaller FontSize, "
                "MarginTop or MarginBottom.",
                config.Paper,
            )
            lines_per_page = 1

        pages = [
            lines[start : start + lines_per_page]
            for start in range(0, len(lines), lines_per_page)
        ]

        if any(
            layout.margin_left + font.getlength(line) > base.width for line in lines
        ):
            logger.warning(
                "Some lines run past the right edge of the %s page. "
                "Use a smaller MaxLineLength or FontSize.",
                config.Paper,
            )

        def render(index: int) -> Image.Image:
            page = base.copy()
            draw = ImageDraw.Draw(page)
            y = layout.margin_top
            for line in pages[index]:
                draw.text((layout.margin_left, y), line, fill=color, font=font)
                y += line_height
            return page

        return render, len(pages)
