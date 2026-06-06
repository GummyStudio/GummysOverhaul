from bauiv1lib.popup import PopupWindow
import random, os, json, zlib, base64, bascenev1 as bs, bauiv1 as bui# im tuff rigjt


class NativeFigureFileExplorerPopup(PopupWindow):
    """
    Look for stuf that ends in .figureplayer
    """
    def __init__(self, on_file_selected_callback: callable):

        self._callback = on_file_selected_callback
        self._width = 480
        self._height = 370
        super().__init__(
            position=(0,0),
            size=(
                self._width,
             self._height
            ),
            bg_color=None
        )

        bui.textwidget(
            parent=self.root_widget,
            position=(self._width * 0.5, self._height - 25),
            size=(0, 0),
            text="Select Figure Profile",
            scale=1.2,
            h_align='center',
            v_align='center'
        )

        self._scroll = bui.scrollwidget(
            parent=self.root_widget,
            position=(30, 75),
            size=(self._width - 60, self._height - 120)
        )
        self._sub_container = bui.containerwidget(
            parent=self._scroll,
            size=(self._width - 80, 20),
            background=False
        )

  
        mods_dir = bui.app.env.python_directory_user
       
            
        files = []
        if os.path.exists(mods_dir):
            files = [f for f in os.listdir(mods_dir) if f.endswith('.figureplayer')]

        y_offset = 10
        if not files:
            bui.textwidget(
                parent=self._sub_container,
                position=((self._width - 80) * 0.5, -60),
                size=(0, 0),
                text="Its empty in here...\nHave you put your\nfiles in your mods folder?",
                scale=0.85,
                color=(1.0, 1.0, 1.0, 0.5),
                h_align='center',
                v_align='center'
            )
        else:
            
            total_height = len(files) * 48.0 + 20.0
            y_offset = total_height - 50.0

            for file_name in files:
                display_name = file_name.replace('.figureplayer', '')
                
                bui.buttonwidget(
                    parent=self._sub_container,
                    position=(10, y_offset),
                    size=(self._width - 100, 42),
                    label=display_name,
                    on_activate_call=lambda f=file_name: self._confirm_selection(mods_dir, f)
                )
                y_offset -= 48.0

        bui.containerwidget(edit=self._sub_container, size=(self._width - 80, total_height))
       
        self._cancel_button = bui.buttonwidget(
            parent=self.root_widget,
            position=(self._width * 0.5 - 60, 20),
            size=(120, 40),
            label="Cancel",
            on_activate_call=self._close
        )

        bui.containerwidget(edit=self.root_widget, cancel_button=self._cancel_button)

    def _confirm_selection(self, directory: str, filename: str):
        full_path = os.path.join(directory, filename)

        # Okay check stuff
        data = decrypt(full_path)
        
        if data:
            self._close()
        
            if self._callback:
                self._callback(data)
            
            
            self._callback = None

    def _close(self):
        """Removes the popup cleanly from view."""
        bui.containerwidget(edit=self.root_widget, transition='out_scale')


def open_file_explorer_native(on_file_selected_callback):
    with bs.ContextRef.empty():

        NativeFigureFileExplorerPopup(on_file_selected_callback)

REQUIRED_KEYS = {
    'nickname', 'character', 'cosmetic', 'level', 'xp', 'color', 'highlight', 
    'abilities', 'behaviors', 'learn', 'targeting', 'extra_data', 'extra_data_2'
}
REQUIRED_BEHAVIORS = {'near', 'runner', 'hold_runner', 'aggressive', 'grounded', 'punch', 'pickup', 'bomb'}
REQUIRED_TARGETING = {'target_random', 'targets_winning', 'targets_losing', 'targets_objective', 'target_revenge'}

def decrypt(pt: str) -> dict | bool:
 
    try:
        with open(pt, 'r', encoding='utf-8') as f:
            b64_data_string = f.read().strip()
            
        cipher_bytes = base64.b64decode(b64_data_string.encode('ascii'))
        
        compressed_bytes = _xor_cipher(cipher_bytes)
        
        json_bytes = zlib.decompress(compressed_bytes)
        json_str = json_bytes.decode('utf-8')
        data = json.loads(json_str)
            
        # Are we sane
        if not isinstance(data, dict):
            raise ValueError
        if not REQUIRED_KEYS.issubset(data.keys()):
            raise ValueError
            
        behaviors = data.get('behaviors', {})
        if not isinstance(behaviors, dict) or not REQUIRED_BEHAVIORS.issubset(behaviors.keys()):
            raise ValueError
            
        targeting = data.get('targeting', {})
        if not isinstance(targeting, dict) or not REQUIRED_TARGETING.issubset(targeting.keys()):
            raise ValueError

        if not isinstance(data['color'], (list, tuple)) or len(data['color']) < 3:
            raise ValueError
            
        return data

    except Exception:
        # corruptioooooon
        bui.getsound('error').play()
        bs.screenmessage('This file is corrupted.', color=(1, 0, 0))
        return False

CIPHER_KEY = b"FigurePlayerSecretKey"

def _xor_cipher(data: bytes) -> bytes:
    key_len = len(CIPHER_KEY)
    return bytes(b ^ CIPHER_KEY[i % key_len] for i, b in enumerate(data))

def create_new_figure_data(
    nickname: str,
    character: str,
    cosmetic: str,
    color: tuple,
    highlight: tuple
):
    mods_dir = bui.app.env.python_directory_user


    data = {
        "nickname": nickname,
        "character": character,
        'cosmetic': cosmetic,
        "level": 1,
        "xp": 0,
        "color": color,
        "highlight": highlight,
        
        "abilities": [None, None, None],
        "learn": True,            # To change data or not
        
        "behaviors": {
            "near": 0.0,          # Target distance lean (high = rush close, low = stay back for bombs)
            "runner": 0.0,        # Tendency to sprint/run
            "hold_runner": 0.0,   # Percentage to actually keep the run button held down
            "aggressive": 0.0,    # Global offensive urge
            "grounded": 0.0,      # How much to stay on the ground

            "punch": 0.0,         # Frequency of punch attacks
            "pickup": 0.0,        # Offensive grab usage
            "bomb": 0.0,          # How often it lets loose with bombs when available
        },
        
        # dynamic targettinggg
        "targeting": {
            "target_random": 1.0,      # Evaluated alongside the next 4 weights
            "targets_winning": 0.0,    # How often to focus the player with the highest score
            "targets_losing": 0.0,     # How often to focus the player with the lowest score
            "targets_objective": 0.0,  # How often to do the objective (ignored in ffa/deathmatch)
            "target_revenge": 0.0      # How often to aggro on whoever hit them/teammate
        },
        
        # Extra data
        "extra_data": {
            "combos": [],
            "startup_routine": None
        },
        "extra_data_2": {},

        # to prevent the same figure from joining same games
        "id": random.randint(
            1, 
            99999999999999999999999999999999999999999999999999999999999
            )
    }

    
  
        
    safe_name = "".join([c for c in nickname if c.isalnum()]).strip()
    if not safe_name:
        safe_name = "figure"
        
    file_name = f"{safe_name}.figureplayer"
    target_path = os.path.join(mods_dir, file_name)

    if os.path.exists(target_path):
        bui.getsound('error').play()
        bs.screenmessage(f"An Amiibo named '{file_name}' already exists!", color=(1, 0, 0))
        return False

    try:
        json_str = json.dumps(data, indent=4)
        json_bytes = json_str.encode('utf-8')
        
        compressed_bytes = zlib.compress(json_bytes)
        
        ciphered_bytes = _xor_cipher(compressed_bytes)
        
        final_b64_string = base64.b64encode(ciphered_bytes).decode('ascii')

        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(final_b64_string)
            
        bui.getsound('gunCocking').play()
        bs.screenmessage(f"Created {data['nickname']} in Mods folder!", color=(0.3, 1, 0.5))
        return True
    except Exception as e:
        print(f"[Figure Player] Figure Encryption Save Error: {e}")
        bui.getsound('error').play()
        bs.screenmessage("Failed. Try again.", color=(1, 0, 0))
        return False
    
ABILITIES_AND_COST = {
            'Longer Invincibility Respawn': 3,
            'Great Auto B2B Charger': 3,
            'Auto Negative Bombs': 3,
            'Auto Sticky Bombs': 2,
            'Auto Impact-Bombs': 2,
            'Auto Ice Bombs': 2,
            'Auto Totem of Undying': 2,
            'Stronger Powerup Magnet': 2,
            'Critical-Health Invincibility': 2,
            'Critical-Health Defense': 2,
            'Auto B2B Charger': 2,
            'B2B Damage ↑': 1,
            'B2B Damage ↑↑': 2,
            'B2B Damage ↑↑↑↑': 3,
            'Auto Impulse-Grendades': 2,
            'Auto Electric-Bombs': 2,
            'Auto Lightning Bombs': 2,
            'Auto Random Bombs': 2,
            'Punch Scale ↑': 1,
            'Impact Scale ↓': 1,
            'Bomb Radius ↑': 1,
            'Health on Kill': 1,
            'Max Health ↑↑': 1,
            'Shield Decay ↓': 1,
            'Shield Health ↑': 1,
            'Powerup Magnet': 2,
            'Stronger Powerup Magnet': 3,
            'Critical-Health Shields': 1,
            'Critical-Health Gloves': 1
        }


