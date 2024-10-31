"""Module for ansi escape codes."""

import sys
from typing import Any, Literal, Union, Callable, Tuple, List, Dict
from dataclasses import dataclass, field
from random import choice
from copy import copy, deepcopy


_colors = Literal[
    'default',
    'black', 'bright_black',
    'blue', 'bright_blue',
    'cyan', 'bright_cyan',
    'green', 'bright_green',
    'magenta', 'bright_magenta',
    'red', 'bright_red',
    'white', 'bright_white',
    'yellow', 'bright_yellow',
]

_ansi_codes = {
    'default': 39,
    'black': 30, 'bright_black': 90,
    'red': 31, 'bright_red': 91,
    'green': 32, 'bright_green': 92,
    'yellow': 33, 'bright_yellow': 93,
    'blue': 34, 'bright_blue': 94,
    'magenta': 35, 'bright_magenta': 95,
    'cyan': 36, 'bright_cyan': 96,
    'white': 37, 'bright_white': 97,
}


@dataclass
class RGB:
    """Class for setting RGB color."""

    red: int
    green: int
    blue: int

    def __str__(self):
        return self.to_hex()

    def __add__(self, other):
        """
        Add two RGB objects.

        Parameters:
            - `other` (RGB): The RGB object to add to self.

        Returns:
            - RGB: A new RGB object representing the average color between self and other.
        """
        if isinstance(other, RGB):
            new_red = (self.red + other.red) / 2
            new_green = (self.green + other.green) / 2
            new_blue = (self.blue + other.blue) / 2
            return RGB(new_red, new_green, new_blue)
        else:
            raise TypeError("Unsupported operand type for +")

    def test(self) -> None:
        """Print color preview on console."""
        print(f'\033[38;2;{self.red};{self.green};{self.blue}m' + self.to_hex() + '\033[0m')

    def to_hex(self) -> str:
        """Convert RGB color to hexadecimal."""
        return "#{:02X}{:02X}{:02X}".format(self.red, self.green, self.blue)

    def to_dict(self) -> Dict:
        """Convert RGB color object to dictionary."""
        return self.__dict__

    @classmethod
    def from_dict(self, data):
        """Convert dictionary to RGB color object."""
        return self(data['red'], data['green'], data['blue'])


@dataclass(init=False)
class Ansi:
    """Class for creating ANSI escape codes."""

    def __init__(
        self,
        fore: Union[_colors, RGB] = 'default',
        back: Union[_colors, RGB] = 'default',
        bold: bool = False,
        dim: bool = False,
        italic: bool = False,
        underline: bool = False,
        strikethrough: bool = False,
        inverse: bool = False,
        reset: bool = True,
    ):
        """
        Initializes an instance of Ansi.

        Parameters:
            - `fore` (Union[_colors, RGB]): Foreground color, either a named color or RGB value. (default is 'default')
            - `back` (Union[_colors, RGB]): Background color, either a named color or RGB value. (default is 'default')
            - `bold` (bool): Flag for bold text. (default is False)
            - `dim` (bool): Flag for dimmed text. (default is False)
            - `italic` (bool): Flag for italicized text. (default is False)
            - `underline` (bool): Flag for underlined text. (default is False)
            - `strikethrough` (bool): Flag for strikethrough text. (default is False)
            - `inverse` (bool): Flag for inverted text. (default is False)
            - `reset` (bool): Flag to reset formatting to default after text. (default is True)
        """
        self.fore = fore
        self.back = back
        self.bold = bold
        self.dim = dim
        self.italic = italic
        self.underline = underline
        self.strikethrough = strikethrough
        self.inverse = inverse
        self.reset = reset

    def __str__(self) -> str:
        """Return the ANSI escape code string representation."""
        return self.string

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Ansi):
            return NotImplemented
        return (
            self.fore == other.fore and
            self.back == other.back and
            self.bold == other.bold and
            self.dim == other.dim and
            self.italic == other.italic and
            self.underline == other.underline and
            self.strikethrough == other.strikethrough and
            self.inverse == other.inverse and
            self.reset == other.reset
        )

    def __add__(self, other):
        if isinstance(other, str):
            result = '\033[39;49;0m' + self.string + other + ('\033[39;49;0m' if self.reset else '')
            return result
        elif isinstance(other, Ansi):
            concat_ansi = Ansi(
                fore=other.fore if self.fore == 'default' else self.fore,
                back=other.back if self.back == 'default' else self.back,
                bold=self.bold or other.bold,
                dim=self.dim or other.dim,
                italic=self.italic or other.italic,
                underline=self.underline or other.underline,
                strikethrough=self.strikethrough or other.strikethrough,
                inverse=self.inverse or other.inverse
            )
            return concat_ansi
        else:
            raise TypeError(f"Unsupported operand type(s) for +: 'Ansi' and {type(other)}")

    def __radd__(self, other: str) -> str:
        if isinstance(other, str):
            result = other + '\x1b[39;49;0m' + self.string
            return result
        else:
            raise TypeError(f"Unsupported operand type(s) for +: '{type(other)}' and 'Ansi'")

    def __call__(self, *values: object, sep: str = ' ') -> str:
        """
        Callable method to concatenate Ansi with values.

        Parameters:
            - `*values`: Values to concatenate with Ansi.
            - `sep` (str): Separator between values. (default is ' ').

        Returns:
            - (str): The concatenated result.
        """
        val = [str(i) for i in values]
        value = sep.join(val)
        return self.string + value + '\033[39;49;0m'

    @property
    def string(self) -> str:
        """
        Property method that generates the ANSI escape code string based on the attribute values.

        Returns:
            - (str): The ANSI escape code string.
        """
        if isinstance(self.fore, str): # Foreground color
            fg = f'\033[{_ansi_codes[self.fore]}m'
        else:
            fg = f'\033[38;2;{self.fore.red};{self.fore.green};{self.fore.blue}m'

        if isinstance(self.back, str): # Background color
            bg = f'\033[{_ansi_codes[self.back] + 10}m'
        else:
            bg = f'\033[48;2;{self.back.red};{self.back.green};{self.back.blue}m'

        b = ';1' if self.bold else '' # Bold
        d = ';2' if self.dim else '' # Dim
        i = ';3' if self.italic else '' # Italic
        u = ';4' if self.underline else '' # Underline
        s = ';9' if self.strikethrough else '' # Strikethrough
        inv = ';7' if self.inverse else '' # Invert

        styles = f'\033[0{b}{i}{u}{s}{d}{inv}m' if any([b, d, i, u, s, inv]) else '\033[0m' # Styles

        return styles + fg + bg

    def test(self, text: str = "Hello World!") -> None:
        """
        Print a test string with the current ANSI formatting.

        Parameters:
            - `text` (str): The text to format and print. (default is 'Hello World!').
        """
        value = self.string + text + '\033[39;49;0m'
        print(value)

    def encode(self) -> bytes:
        """
        Encode the ANSI escape code string.

        Returns:
            - (bytes): The encoded ANSI escape code string.
        """
        return self.string.encode()

    def set_fore(self, fore: Union[_colors, RGB]):
        """Set the foreground color and returns modified style object."""
        new_style = copy(self)
        new_style.fore = fore
        return new_style

    def set_back(self, back: Union[_colors, RGB]):
        """Set the background color and returns modified style object."""
        new_style = copy(self)
        new_style.back = back
        return new_style

    def set_bold(self, bold: bool):
        """Set the bold attribute and returns modified style object."""
        new_style = copy(self)
        new_style.bold = bold
        return new_style

    def set_dim(self, dim: bool):
        """Set the dim attribute and returns modified style object."""
        new_style = copy(self)
        new_style.dim = dim
        return new_style

    def set_italic(self, italic: bool):
        """Set the italic attribute and returns modified style object."""
        new_style = copy(self)
        new_style.italic = italic
        return new_style

    def set_underline(self, underline: bool):
        """Set the underline attribute and returns modified style object."""
        new_style = copy(self)
        new_style.underline = underline
        return new_style

    def set_strikethrough(self, strikethrough: bool):
        """Set the strikethrough attribute and returns modified style object."""
        new_style = copy(self)
        new_style.strikethrough = strikethrough
        return new_style

    def set_inverse(self, inverse: bool):
        """Set the inverse attribute and returns modified style object."""
        new_style = copy(self)
        new_style.inverse = inverse
        return new_style

    def to_dict(self) -> Dict:
        """Return a dictionary representation of the style object."""
        new = deepcopy(self)
        if isinstance(new.fore, RGB):
            new.fore = new.fore.to_dict()
        if isinstance(new.back, RGB):
            new.back = new.back.to_dict()
        return new.__dict__

    @classmethod
    def from_dict(self, data: Dict):
        """Create a style object from a dictionary representation."""
        fore = data.get('fore', 'default')
        back = data.get('back', 'default')
        if not isinstance(fore, str):
            fore = RGB.from_dict(fore)
        if not isinstance(back, str):
            back = RGB.from_dict(back)
        return self(
            fore=fore,
            back=back,
            bold=data.get('bold', False),
            dim=data.get('dim', False),
            italic=data.get('italic', False),
            underline=data.get('underline', False),
            strikethrough=data.get('strikethrough', False),
            inverse=data.get('inverse', False),
            reset=data.get('reset', True),
        )


class Terminal:
    """
    A utility class for interacting with the terminal.

    Methods:
    --------
        - `get_terminal_size() -> Any`:
            Retrieves the size of the terminal window.

        - `move_left(n: int = 1) -> None`:
            Moves the cursor to the left by `n` characters.

        - `move_right(n: int = 1) -> None`:
            Moves the cursor to the right by `n` characters.

        - `move_up(n: int = 1) -> None`:
            Moves the cursor up by `n` lines.

        - `move_down(n: int = 1) -> None`:
            Moves the cursor down by `n` lines.

        - `move_to(x: int, y: int) -> None`:
            Moves the cursor to the specified position (`x`, `y`) in the terminal window.

        - `hide() -> None`:
            Hides the terminal cursor.

        - `show() -> None`:
            Shows the terminal cursor.

        - `move_line_beginning() -> None`:
            Moves the cursor to the beginning of the current line.

        - `clear() -> None`:
            Clears the entire terminal screen.

        - `clear_line() -> None`:
            Clears the current line.

        - `ding() -> None`:
            Produces a beep sound in the terminal.

        - `scroll_up(n: int = 1) -> None`:
            Scrolls the terminal window up by `n` lines.

        - `scroll_down(n: int = 1) -> None`:
            Scrolls the terminal window down by `n` lines.

        - `save() -> None`:
            Saves the current position of the terminal cursor.

        - `load() -> None`:
            Restores the previously saved position of the terminal cursor.

        - `fix_windows_console() -> None`:
            Enables ANSI escape code support in the Windows console.
            This function is specific to Windows and is automatically called if necessary.
    """

    @staticmethod
    def get_terminal_size() -> object:
        """Retrieve the size of the terminal window."""
        from os import get_terminal_size as gts
        return gts()

    @staticmethod
    def move_left(n: int = 1) -> None:
        """Move the cursor to the left by `n` characters."""
        sys.stdout.write(f"\033[{n}D")
        sys.stdout.flush()

    @staticmethod
    def move_right(n: int = 1) -> None:
        """Move the cursor to the right by `n` characters."""
        sys.stdout.write(f"\033[{n}C")
        sys.stdout.flush()

    @staticmethod
    def move_up(n: int = 1) -> None:
        """Move the cursor up by `n` lines."""
        sys.stdout.write(f"\033[{n}A")
        sys.stdout.flush()

    @staticmethod
    def move_down(n: int = 1) -> None:
        """Move the cursor down by `n` lines."""
        sys.stdout.write(f"\033[{n}B")
        sys.stdout.flush()

    @staticmethod
    def move_to(x: int, y: int) -> None:
        """Move the cursor to the specified position (`x`, `y`) in the terminal window."""
        sys.stdout.write(f"\033[{y};{x}H")
        sys.stdout.flush()

    @staticmethod
    def hide() -> None:
        """Hide the terminal cursor."""
        sys.stdout.write("\033[?25l")
        sys.stdout.flush()

    @staticmethod
    def show() -> None:
        """Show the terminal cursor."""
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()

    @staticmethod
    def move_line_beginning() -> None:
        """Move the cursor to the beginning of the current line."""
        sys.stdout.write("\r")
        sys.stdout.flush()

    @staticmethod
    def clear() -> None:
        """Clear the entire terminal screen."""
        sys.stdout.write("\033[2J\033[H")
        sys.stdout.flush()

    @staticmethod
    def clear_line() -> None:
        """Clear the current line."""
        sys.stdout.write("\r\033[K")
        sys.stdout.flush()

    @staticmethod
    def ding() -> None:
        """Produce a beep sound in the terminal."""
        sys.stdout.write("\007")
        sys.stdout.flush()

    @staticmethod
    def scroll_up(n: int = 1) -> None:
        """Scroll the terminal window up by `n` lines."""
        sys.stdout.write(f"\033[{n}T")
        sys.stdout.flush()

    @staticmethod
    def scroll_down(n: int = 1) -> None:
        """Scroll the terminal window down by `n` lines."""
        sys.stdout.write(f"\033[{n}S")
        sys.stdout.flush()

    @staticmethod
    def save() -> None:
        """Save the current position of the terminal cursor."""
        sys.stdout.write("\033[s")
        sys.stdout.flush()

    @staticmethod
    def load() -> None:
        """Restore the previously saved position of the terminal cursor."""
        sys.stdout.write("\033[u")
        sys.stdout.flush()

    @staticmethod
    def fix_windows_console() -> None:
        """
        Enable ANSI escape code support in the Windows console.
        This function is specific to Windows and is automatically called if necessary.
        """
        import platform, ctypes
        if platform.system().lower() == 'windows':
            try:
                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            except Exception as e:
                print(f"Failed to enable ANSI support on Windows: {e}")


_modes = Literal["by letter", "by word", "by percent", "random"]


def remove_ansi(input_string: str) -> str:
    """Remove ANSI escape codes from an input string."""
    import re
    ansi_escape = re.compile(r'\033\[[0-9;]+m')
    return ansi_escape.sub('', input_string)

def add(text: str, x: int = 0, y: int = 0) -> None:
    """
    Add text to the terminal at specified coordinates.

    Parameters:
        - `x` (int): The x-coordinate on the terminal where the text will start.
        - `y` (int): The y-coordinate on the terminal where the text will start.
        - `text` (str): The text to display at the specified coordinates. The text can contain multiple lines.
    """
    Terminal.save()
    Terminal.move_to(x, y)
    for i, line in enumerate(text.split('\n')):
        print(line, end='')
        Terminal.move_to(x, y+i)
    Terminal.load()



# @dataclass
# class Style:
#     """
#     Class that represent some ansi text pattern
#     """
#     pattern: List[Ansi] = field(default_factory=lambda: [])
#     mode: _modes = "by letter"
#     number: int = 1
#     start: int = 0

#     box: int | None = None
#     justify: Literal["left", "center", "right"] = "left"

#     text_func: Callable | None = None
#     specials: Dict[int, str] = field(default_factory=lambda: {})
#     prefix: str = ""
#     surfix: str = ""
#     letter_spacing: str = ""
#     letter_func: Callable | None = None
#     word_spacing: Union[str, None] = None
#     word_func: Callable | None = None

#     def __add__(self, other):
#         if isinstance(other, Style):
#             new_style = Style(
#                 pattern = self.pattern + other.pattern,
#                 mode = self.mode,
#                 number = self.number if not self.number else self.number,
#                 start = self.start if not self.start else self.start,
#                 box = other.box if not self.box else self.box,
#                 justify = other.justify if self.justify == "left" else self.justify,
#                 text_func = other.text_func if not self.text_func else self.text_func,
#                 specials = self.specials.update(other.specials),
#                 prefix = other.prefix if not self.prefix else self.prefix,
#                 surfix = self.surfix if not other.surfix else other.surfix,
#                 letter_spacing = other.letter_spacing if not self.letter_spacing else self.letter_spacing,
#                 letter_func = other.letter_func if not self.letter_func else self.letter_func,
#                 word_spacing = other.word_spacing if not self.word_spacing else self.word_spacing,
#                 word_func = other.word_func if not self.word_func else self.word_func,
#             )
#             return new_style
#         else:
#             raise TypeError(f"Unsupported operand type(s) for +: 'Style' and {type(other)}")

#     def __call__(self, text: str):
#         return self.string(text)

#     def string(self, text: str) -> str:
#         """
#         Generates a styled string based on the specified pattern and settings.

#         Parameters:
#             - text (str): The input text to be styled.

#         Returns:
#             - str: The final styled result.
#         """
#         def l_getter(string: str):
#             left = ""
#             for char in string:
#                 if char.isspace():
#                     left += char
#                 else:
#                     return left

#         def r_getter(string:str):
#             right = ""
#             for char in string[::-1]:
#                 if char.isspace():
#                     right += char
#                 else:
#                     return right[::-1]

#         def add_pattern(text):
#             length = len(self.pattern)
#             new_text = ""
#             wait = 0

#             if self.mode == 'by letter':
#                 for i, char in enumerate(text, self.start * self.number):
#                     if char.isspace():
#                         new_text += char
#                         wait += 1
#                     else:
#                         new_text += self.pattern[(i - wait) // self.number % length] + char
#                 return new_text

#             elif self.mode == 'by word':
#                 new = []
#                 adding = 0
#                 start = 0
#                 for i, char in enumerate(text):
#                     if char.isspace():
#                         adding += 1
#                     if adding > 0 and not char.isspace():
#                         adding = 0
#                         new.append(text[start:i])
#                         start = i

#                 for i, char in enumerate(new, self.start * self.number):
#                     if char.isspace():
#                         new_text += char
#                         wait += 1
#                     else:
#                         new_text += self.pattern[(i - wait) // self.number % length] + char
#                 return new_text

#             elif self.mode == 'by percent':
#                 length = length * self.number

#                 constructed = []
#                 for line in text.split("\n"):
#                     left = l_getter(line) if l_getter(line) else ""
#                     right = r_getter(line) if r_getter(line) else ""
#                     sline = line.strip()
#                     text_len = len(sline) // length
#                     form = [text_len for i in range(length)]

#                     for i in [i // 2 if i % 2 == 0 else -i // 2 for i in range((len(sline) - (text_len * length)))]: # 0, -1, 1, -2, 2 ...
#                         form[i] += 1

#                     divided = []
#                     start = 0
#                     for i in form:
#                         divided.append(sline[start:start+i])
#                         start += i

#                     new_text = ""
#                     wait = 0
#                     for i, frag in enumerate(divided, self.start):
#                         if frag.isspace():
#                             new_text += frag
#                             wait += 1
#                         else:
#                             new_text += self.pattern[int((i - wait) % (length / self.number))] + frag

#                     new_text = left + new_text + right
#                     constructed.append(new_text)

#                 return "\n".join(constructed)

#             elif self.mode == 'random':
#                 new_random = choice(self.pattern)

#                 for i, char in enumerate(text):
#                     if i % self.number == 0:
#                         new_random = choice(self.pattern)

#                     if char.isspace():
#                         new_text += char
#                     else:
#                         new_text += new_random + char
#                 return new_text
            
#         def add_specials(text):
#             result = text
#             if self.specials:
#                 i = 0
#                 for index, val in dict(sorted(self.specials.items())).items():
#                     result = result[:index+i] + val + result[index+i:]
#                     i += len(val)
#             return result

#         def add_chars(text):
#             splited = []
#             whites = ""
#             normal = ""

#             # Adding function
#             if self.text_func:
#                 func_text = self.text_func(text)
#             else:
#                 func_text = text

#             # Spliting text into words and whitespaces
#             for char in func_text:
#                 if char.isspace():
#                     if normal: splited.append(normal)
#                     normal = ""
#                     whites += char
#                 else:
#                     if whites: splited.append(whites)
#                     whites = ""
#                     normal += char
#             if normal: splited.append(normal)
#             if whites: splited.append(whites)

#             # Adding letter and word functions, spacing, left decorations and right decorations
#             new = ""
#             for i in splited:
#                 if i.isspace():
#                     if self.word_spacing is None:
#                         new += i
#                     else:
#                         new += self.word_spacing
#                 else:
#                     sub_new = []
#                     for char in i:
#                         if self.letter_func:
#                             sub_new.append(self.letter_func(char))
#                         else:
#                             sub_new.append(char)
#                     sub_new = self.letter_spacing.join(sub_new)
#                     if self.word_func:
#                         new += self.word_func(sub_new)
#                     else:
#                         new += sub_new

#             return new

#         def add_box(text):
#             if self.box:
#                 aligned = []
#                 for line in text.split("\n"):
#                     if self.justify == "left":
#                         aligned.append(f"{line: <{self.box}}")
#                     elif self.justify == "center":
#                         aligned.append(f"{line: ^{self.box}}")
#                     elif self.justify == "right":
#                         aligned.append(f"{line: >{self.box}}")
#                     else:
#                         aligned.append(f"{line:self.box}")
#                 return "\n".join(aligned)
#             else:
#                 return text

#         result = add_specials(text)
#         result = add_chars(result)
#         result = self.prefix + result + self.surfix
#         result = add_box(result)
#         result = add_pattern(result)

#         return result

#     def set_letter_func(self, letter_func: Callable):
#         """ Sets functian that will execute for every letter and returns modified style Object. """
#         new_style = copy(self)
#         new_style.letter_func = letter_func
#         return new_style

#     def set_word_func(self, word_func: Callable):
#         """ Sets function that will execute for every word and returns modified style Object. """
#         new_style = copy(self)
#         new_style.word_func = word_func
#         return new_style
    
#     def set_text_func(self, text_func: Callable):
#         """ Sets function that will execute for entire text and returns modified style Object. """
#         new_style = copy(self)
#         new_style.text_func = text_func
#         return new_style

#     def set_letter_spacing(self, letter_spacing: str):
#         """ Sets spacing between letters and returns modified style Object. """
#         new_style = copy(self)
#         new_style.letter_spacing = letter_spacing
#         return new_style

#     def set_word_spacing(self, word_spacing: Union[str, None]):
#         """
#         Sets spacing between words and returns modified style Object. None means default text spacing.

#         Examples:
#             >>> text = "Hello   World   !"

#             >>> style = style.set_word_spacing(' ')
#             >>> print(style(text))
#             Hello World !

#             >>> style = style.set_word_spacing(None)
#             >>> print(style(text))
#             Hello   World   !
#         """
#         new_style = copy(self)
#         new_style.word_spacing = word_spacing
#         return new_style

#     def set_prefix(self, prefix: str):
#         """ Sets prefix for the text and returns modified style Object. """
#         new_style = copy(self)
#         new_style.prefix = prefix
#         return new_style

#     def set_surfix(self, surfix: str):
#         """ Sets surfix for the text and returns modified style Object. """
#         new_style = copy(self)
#         new_style.surfix = surfix
#         return new_style

#     def set_mode(self, mode: _modes):
#         """
#         Sets how the text will be styled and returns modified style Object.

#         Parameters:
#             - mode (Literal["by letter", "by word", "by percent", "random"]):
#                 - "by letter" - each letter will be styled separately.
#                 - "by word"  - each word will be styled separately.
#                 - "by percent" - the text will be styled by percent of the text length.
#                 - "random" - random style will be applied to each character.
#         """
#         if mode not in ["by letter", "by word", "by percent", "random"]:
#             raise ValueError(f"Mode must be {_modes}.")
#         new_style = copy(self)
#         new_style.mode = mode
#         return new_style

#     def set_pattern(self, pattern: List[Ansi]):
#         """      
#         Sets the pattern that will be cast to text and returns modified style Object.

#         Parameters:
#             - pattern (List(Ansi)):

#         Example:
#             >>> style = style.set_mode("by percent")
#             >>> style = style.set_pattern([Ansi(RGB(255, 0, 0)), Ansi(RGB(0, 255, 0)), Ansi(RGB(0, 0, 255))])
#             >>> print(style("Hello World!"))

#             The result will be "Hello World!", first 4 characters will be red, next 4 will be green and next 4 blue.
#         """
#         new_style = copy(self)
#         new_style.pattern = pattern
#         return new_style

#     def set_number(self, number: int):
#         """
#         Sets number and returns modified style object.
#         A multiplier is used in certain modes to control the repetition of the pattern.
#         For number = 1 and mode = "by letter", one pattern element will be assigned to one letter.
#         For number = 2, one pattern element will be assigned to two consecutive letters, and so on.
#         """
#         new_style = copy(self)
#         new_style.number = number
#         return new_style

#     def set_start(self, start: int):
#         """ Sets ann offset used to control where the pattern application starts and returns modified style object. """
#         new_style = copy(self)
#         new_style.start = start
#         return new_style

#     def set_box(self, box: int | None):
#         """
#         Sets box size for text (after adding special effects like prefix, spacing etc.) and returns modified style object.
#         For example if text have 6 letters, box size is set to 10 and and justify is set to "left", then 4 spaces will be added to the text.
#         If justify is set to "right", then 4 spaces will be added at the beginning of the text.
#         And if justify is set to "center", then 2 spaces will be added at beginning and 2 at the end of the text.
#         """
#         new_style = copy(self)
#         new_style.box = box
#         return new_style
    
#     def set_justify(self, justify: Literal["left", "center", "right"] | None):
#         """ Justifies the output according to the parameter value. """
#         if justify not in ["left", "center", "right"]:
#             raise ValueError('Justification must be either "left", "center", "right" or None.')
#         new_style = copy(self)
#         new_style.justify = justify
#         return new_style


#     def set_for_all_pattern(
#         self,
#         property: Literal[
#             "fore",
#             "back",
#             "bold",
#             "dim",
#             "italic",
#             "underline",
#             "strikethrough",
#         ],
#         value: Any,
#     ):
#         """
#         Set a specified property and value for every element in the pattern and returns modified style object.

#         Parameters:
#             - `property` (Literal["fore", "back", "bold", "dim", "italic", "underline", "strikethrough"]):
#             The property to set for each Ansi element in the pattern.
#             - `value` (any): The value to set for the specified property.
#         """
#         new_pattern = []
#         for ansi in self.pattern:
#             new_ansi = copy(ansi)
#             setattr(new_ansi, property, value)
#             new_pattern.append(new_ansi)

#         new_style = copy(self)
#         new_style.pattern = new_pattern
#         return new_style


# def center(text: str):
#     """Return the centered text."""
#     from shutil import get_terminal_size

#     console_width = get_terminal_size().columns

#     centered = []
#     for line in text.split("\n"):
#         centered.append(f"{line: ^{console_width}}")

#     return "\n".join(centered)


# def reverse(text: str):
#     """Return the reversed text."""
#     return text[::-1]


def adv_gradient(colors: List[Tuple[RGB, int]], steps: int) -> List[RGB]:
    """
    Generate advanced gradient.

    Parameters:
        - `colors` (List[RGB, int]): List of tuples, each tuple with 2 elements:
            - RGB(): Color object.
            - int: Number between 0 and 100 representing the color's percentage placement.
        - `steps` (int): How many ansi object in the list will be returned, the bigger.
          The larger the number, the more accurate but more complicated the gradient.

    Returns:
        - List[RGB]: List that can be converted to ansi pattern and then used as a pattern in style object.

    Examples:
        >>> adv_gradient([(RGB(255, 0, 0), 10), (RGB(0, 255, 0), 30), (RGB(0, 0, 255), 70)], 100)
        # 0% - 10%: red, 10% - 30%: red-green, 30% - 70%: green-blue, 70% - 100%: blue
    """
    sorted_cols = sorted(colors, key=lambda x: x[1]) # Sort colors by percentage

    # Adding percentages marks
    col_arr_perc = []
    if not sorted_cols[0][1] == 0: # Add 0 at beginning if it's not there
        col_arr_perc.append(0)

    for i in sorted_cols:
        col_arr_perc.append(i[1])

    if not sorted_cols[-1][1] == 100: # Add 100 at beginning if it's not there
        col_arr_perc.append(100)

    # Calculate percentage for each color
    perc = []
    for i, n in enumerate(col_arr_perc[1:], 1):
          perc.append(n - col_arr_perc[i-1])

    # Calculate amount of steps for each color
    steps_per = []
    for i in perc:
        steps_per.append(round((i / sum(perc)) * steps))
    
    del perc, col_arr_perc

    # Create gradient based on its percentage
    result = []
    if not sorted_cols[0][1] == 0: # Add no-gradient color at the beginning if it was set
        for _ in range(steps_per[0]):
            result.append(sorted_cols[0][0])
        steps_per.pop(0)
    
    if not sorted_cols[-1][1] == 100: # Delete the last index if its 100
        last = steps_per.pop(-1)

    for i, steps in enumerate(steps_per): # Add gradient in the middle
        result = result + gradient(sorted_cols[i][0], sorted_cols[i+1][0], steps)

    if not sorted_cols[-1][1] == 100: # Add no-gradient color at the end if it was set
        steps_per.append(last)
        for _ in range(steps_per[-1]):
            result.append(sorted_cols[-1][0])

    return result


def gradient(color1: RGB, color2: RGB, steps: int) -> List[RGB]:
    """Generate gradient."""
    gradient_colors = []

    for step in range(steps):
        # Interpolate the RGB values for each step
        r = int(color1.red + (color2.red - color1.red) * step / (steps - 1))
        g = int(color1.green + (color2.green - color1.green) * step / (steps - 1))
        b = int(color1.blue + (color2.blue - color1.blue) * step / (steps - 1))

        gradient_colors.append(RGB(r, g, b))

    return gradient_colors


def to_ansi(colors: List[RGB], target: Literal["fore", "back"] = "fore") -> List[Ansi]:
    """
    Convert a list of RGB colors to a list of Ansi colors for foreground or background styling.

    Parameters:
        - `colors` (List[RGB]): List of RGB colors to be converted.
        - `target` (Literal["fore", "back"], optional): The target styling, either "fore" (foreground) or "back" (background).
          Defaults to "fore".

    Returns:
        - List[Ansi]: List of Ansi colors corresponding to the input RGB colors.

    Raises:
        - ValueError: If the target is not "fore" or "back".
    """
    if target not in ["fore", "back"]:
        raise ValueError("target must be \"fore\" or \"back\".")
    result = []
    for color in colors:
        if target == "fore":
            result.append(Ansi(fore=color))
        else:
            result.append(Ansi(back=color))

    return result
