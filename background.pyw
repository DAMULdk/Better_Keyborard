"""
Background BetterKeyboard module, used in background for shortcuts to work.
"""

# Imports
import keyboard as kb
import pyperclip
from time import sleep

# Fancy letter sets
chars = "QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm"
thug_chars = "𝔔𝔚𝔈ℜ𝔗𝔜𝔘ℑ𝔒𝔓𝔄𝔖𝔇𝔉𝔊ℌ𝔍𝔎𝔏ℨ𝔛ℭ𝔙𝔅𝔑𝔐𝔮𝔴𝔢𝔯𝔱𝔶𝔲𝔦𝔬𝔭𝔞𝔰𝔡𝔣𝔤𝔥𝔧𝔨𝔩𝔷𝔵𝔠𝔳𝔟𝔫𝔪"
thick_thug_chars = "𝕼𝖂𝕰𝕽𝕿𝖄𝖀𝕴𝕺𝕻𝕬𝕾𝕯𝕱𝕲𝕳𝕵𝕶𝕷𝖅𝖃𝕮𝖁𝕭𝕹𝕸𝖖𝖜𝖊𝖗𝖙𝖞𝖚𝖎𝖔𝖕𝖆𝖘𝖉𝖋𝖌𝖍𝖏𝖐𝖑𝖟𝖝𝖈𝖛𝖇𝖓𝖒"
bold_chars = "𝙌𝙒𝙀𝙍𝙏𝙔𝙐𝙄𝙊𝙋𝘼𝙎𝘿𝙁𝙂𝙃𝙅𝙆𝙇𝙕𝙓𝘾𝙑𝘽𝙉𝙈𝙦𝙬𝙚𝙧𝙩𝙮𝙪𝙞𝙤𝙥𝙖𝙨𝙙𝙛𝙜𝙝𝙟𝙠𝙡𝙯𝙭𝙘𝙫𝙗𝙣𝙢"

# Character dictionaries
thug_chars_dict = dict(zip(chars, thug_chars))
thick_thug_chars_dict = dict(zip(chars, thick_thug_chars))
bold_chars_dict = dict(zip(chars, bold_chars))

# Assign the desired character set (e.g., bold_chars_dict)
selected_chars_dict = bold_chars_dict

def convert_text(text: str, chars_set: dict) -> str:
    """Converts characters in the text to the chosen style."""
    return ''.join(chars_set.get(char, char) for char in text)

def on_shortcut():
    """Handles the shortcut for converting selected text."""
    kb.press_and_release('ctrl+c')  # Copy selected text
    sleep(0.05)  # Delay to ensure clipboard update
    selected_text = pyperclip.paste() or ""
    
    # Convert the text
    converted_text = convert_text(selected_text, bold_chars_dict)
    
    # Copy converted text back to clipboard and paste
    pyperclip.copy(converted_text)
    kb.press_and_release('ctrl+v')

# Set up shortcut
kb.add_hotkey('ctrl+alt+b', on_shortcut)

kb.wait()

