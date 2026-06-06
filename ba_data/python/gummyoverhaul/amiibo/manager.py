# Released under the MIT License. See LICENSE for details.
#
"""Session and Activity for displaying the main menu bg."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING, Callable, override


import bascenev1 as bs
import bauiv1 as bui
from bauiv1lib.popup import PopupWindow, PopupMenu
from bauiv1lib.colorpicker import ColorPicker
from bauiv1lib.characterpicker import CharacterPicker, CharacterPickerDelegate
from bascenev1lib.actor.spaz import Spaz
import os, json, base64, zlib, _babase
from .helpers import _xor_cipher, ABILITIES_AND_COST as ability_costs

import babase
from bascenev1lib.gameutils import SharedObjects


if TYPE_CHECKING:
    from typing import Any


class FigureCreationWindow(PopupWindow, CharacterPickerDelegate):
    
    def __init__(self, origin_widget: bui.Widget | None = None):
        assert bui.app.classic is not None
        
        self._width = 680.0
        self._height = 420.0
        
        super().__init__(
            position=(0, 0),
            size=(self._width, self._height), 
            bg_color=None
        )

        self._color = (0.4, 1.0, 0.4)
        self._highlight = (1.0, 1.0, 0.4)
        self._character = 'Spaz'
        self._cosmetic = None
        
        #get
        from bascenev1lib.actor import spazappearance
        self._spazzes = spazappearance.get_appearances()
        self._spazzes.sort()

        self._cancel_button = bui.buttonwidget(
            parent=self.root_widget, position=(40, self._height - 65), size=(130, 48),
            label=bui.Lstr(resource='cancelText'), on_activate_call=self._close
        )
        
        self._create_button = bui.buttonwidget(
            parent=self.root_widget, position=(self._width - 170, self._height - 65), size=(130, 48),
            label="Create", color=(0.2, 0.7, 0.3)
        )
        bui.buttonwidget(edit=self._create_button, on_activate_call=self._save_and_encrypt)

        bui.textwidget(
            parent=self.root_widget, position=(self._width * 0.5, self._height - 40), size=(0, 0),
            text="Create Figure Player", scale=1.1, color=(0.3, 1.0, 0.6), h_align='center', v_align='center'
        )

        bui.textwidget(
            parent=self.root_widget, text="Nickname", position=(70, self._height - 130),
            size=(0, 0), h_align='left', v_align='center', color=(0.7, 0.7, 0.7)
        )
        
        names = bs.get_random_names()
        default_rand_name = names[random.randrange(len(names))]
        self._text_field = bui.textwidget(
            parent=self.root_widget, position=(220, self._height - 150), size=(260, 40),
            text=default_rand_name, h_align='left', v_align='center', editable=True, max_chars=14,
            color=(0.9, 0.9, 0.9), on_return_press_call=bui.Call(self._create_button.activate)
        )

        v_slot = self._height - 260
        
        self._character_button = bui.buttonwidget(
            parent=self.root_widget, autoselect=True, position=(self._width * 0.5 - 50, v_slot),
            size=(100, 100), label='', color=(1, 1, 1), mask_texture=bui.gettexture('characterIconMask'),
            on_activate_call=self._open_character_picker
        )
        
        bui.textwidget(
            parent=self.root_widget, h_align='center', v_align='center', position=(self._width * 0.5, v_slot - 15),
            size=(0, 0), text="Character", scale=0.65, color=(0.5, 0.5, 0.5)
        )

        self._color_button = bui.buttonwidget(
            parent=self.root_widget, autoselect=True, position=(self._width * 0.5 - 190, v_slot + 10),
            size=(70, 70), color=self._color, label='', button_type='square',
            on_activate_call=lambda: self._make_picker('color', self._color_button.get_screen_space_center())
        )
        bui.textwidget(
            parent=self.root_widget, h_align='center', v_align='center', position=(self._width * 0.5 - 155, v_slot - 15),
            size=(0, 0), text="Color", scale=0.7, color=bui.app.ui_v1.title_color
        )

        self._highlight_button = bui.buttonwidget(
            parent=self.root_widget, autoselect=True, position=(self._width * 0.5 + 120, v_slot + 10),
            size=(70, 70), color=self._highlight, label='', button_type='square',
            on_activate_call=lambda: self._make_picker('highlight', self._highlight_button.get_screen_space_center())
        )
        bui.textwidget(
            parent=self.root_widget, h_align='center', v_align='center', position=(self._width * 0.5 + 155, v_slot - 15),
            size=(0, 0), text="Highlight", scale=0.7, color=bui.app.ui_v1.title_color
        )

        cfg = bui.app.config
        self._character_cosmetics = {
            'Spaz': ['None'], 'Penny': ['None'], 'Amar': ['None'], 'Orangecap': ['None'],
            'Snake Shadow': ['None'], 'Mel': ['None'], 'Jack Morgan': ['None'],
            'Agent Johnson': ['None'], 'Easter Bunny': ['None']
        }

        if cfg.get('ownedCosmetic_SpazEXE'): self._character_cosmetics['Spaz'].append('Spaz.EXE')
        if cfg.get('ownedCosmetic_StarHoodie'): self._character_cosmetics['Penny'].append('Star Hoodie')
        if cfg.get('ownedCosmetic_Insane'): self._character_cosmetics['Amar'].append('Full-Insanity')
        if cfg.get('ownedCosmetic_Bluecap'): self._character_cosmetics['Orangecap'].append('Blue Cap')
        if cfg.get('ownedCosmetic_Melling'): self._character_cosmetics['Mel'].append('Melling')
        if cfg.get('ownedCosmetic_Spazling'): self._character_cosmetics['Spaz'].append('Spazling')
        if cfg.get('ownedCosmetic_Ninjaling'): self._character_cosmetics['Snake Shadow'].append('Ninjaling')
        if cfg.get('ownedCosmetic_Sal'):
            self._character_cosmetics['Spaz'].extend(['Salvatore', 'Sal but with a voice'])
        if cfg.get('ownedScoldy'): self._character_cosmetics['Spaz'].append('Scoldy')
        if cfg.get('ownedJolluNinja_Cosmetic'): self._character_cosmetics['Snake Shadow'].append('Jolly')
        if cfg.get('ownedHHH_amarCosmetic'): self._character_cosmetics['Amar'].append('Horseless Headless Horseman')
        if cfg.get('ownedGummyVoiceSpaz_Cosmetic'): self._character_cosmetics['Spaz'].append('Gummy Voice Spaz')
        if cfg.get('ownedGummyVoiceJack_Cosmetic'): self._character_cosmetics['Jack Morgan'].append('Gummy Voice Jack')
        if cfg.get('ownedGummyVoiceJack_Cosmetic'): self._character_cosmetics['Agent Johnson'].append('Gummy Voice Agent')
        if cfg.get('ownedYurirblx_Cosmetic'): self._character_cosmetics['Spaz'].append('YBS16')
        if cfg.get('ownedTopHat_Cosmetic'): self._character_cosmetics['Easter Bunny'].append('Tophat')

        self._cosmetic_menu = PopupMenu(
            parent=self.root_widget, position=(self._width * 0.5 - 75, 55), width=150,
            choices=self._character_cosmetics.get(self._character, ['None']),
            current_choice='None', on_value_change_call=self._change_cosmetic
        )
        
        bui.textwidget(
            parent=self.root_widget, h_align='center', v_align='center', position=(self._width * 0.5, 115),
            size=(0, 0), draw_controller=self._cosmetic_menu.get_button(), text='Cosmetic', scale=0.7, color=bui.app.ui_v1.title_color
        )

     
        bui.containerwidget(edit=self.root_widget, cancel_button=self._cancel_button, start_button=self._create_button, selected_child=self._text_field)
        self._update_character_render()
        bs.get_foreground_host_activity().set_music('create_new')

    def _open_character_picker(self) -> None:
        CharacterPicker(
            parent=self.root_widget,
            position=self._character_button.get_screen_space_center(),
            selected_character=self._character,
            delegate=self,
            tint_color=self._color,
            tint2_color=self._highlight,
            include_get_more=False
        )

    def on_character_picker_pick(self, character: str) -> None:
        self._character = character
        
            
        new_choices = self._character_cosmetics.get(self._character, ['None'])
        self._cosmetic_menu._choices = new_choices
        if self._cosmetic not in new_choices:
            self._cosmetic = None
            self._cosmetic_menu.set_choice('None')
            
        self._update_character_render()

    def _make_picker(self, picker_type: str, origin: tuple[float, float]) -> None:
        ColorPicker(
            parent=self.root_widget, position=origin,
            offset=( -100 if picker_type == 'color' else 100, 0),
            initial_color=self._color if picker_type == 'color' else self._highlight,
            delegate=self, tag=picker_type
        )

    def color_picker_selected_color(self, picker: ColorPicker, color: tuple[float, float, float]) -> None:
        if picker.get_tag() == 'color':
            self._color = color
            bui.buttonwidget(edit=self._color_button, color=color)
        else:
            self._highlight = color
            bui.buttonwidget(edit=self._highlight_button, color=color)
        self._update_character_render()

    def color_picker_closing(self, *args) -> None:
        pass
        
    def _change_cosmetic(self, value: str) -> None:
        self._cosmetic = value

    def _update_character_render(self) -> None:
        app = bui.app.classic
        assert app is not None
        
        # Grab properties out of global game appearances matrix setup
        appearance_info = app.spaz_appearances.get(self._character)
        if appearance_info is not None:
            bui.buttonwidget(
                edit=self._character_button,
                texture=bui.gettexture(appearance_info.icon_texture),
                tint_texture=bui.gettexture(appearance_info.icon_mask_texture),
                tint_color=self._color, 
                tint2_color=self._highlight
            )

    def _save_and_encrypt(self) -> None:
        from .helpers import create_new_figure_data

        nickname = bui.textwidget(query=self._text_field)
        if not nickname or not nickname.strip():
            bui.getsound('error').play()
            bs.screenmessage("Nickname cannot be empty.", color=(1.0, 0.3, 0.3))
            return

        create_new_figure_data(
            nickname=nickname.strip(),
            character=self._character,
            cosmetic=self._cosmetic,
            color=self._color,
            highlight=self._highlight
        )
        self._close()

    def _close(self) -> None:
        bs.get_foreground_host_activity().set_music('main')
       
        bui.containerwidget(edit=self.root_widget, transition='out_scale')

class FigureManagerWindow(bui.MainWindow):
    
    def __init__(self):
        platform = bui.app.classic.platform
        self._is_mobile = platform in ('android')

        self._width = 620 if not self._is_mobile else 450
        self._height = 320 if not self._is_mobile else 220

        super().__init__(root_widget=bui.containerwidget(
            size=(self._width, self._height), transition='in_scale', scale=1.0, stack_offset=(0, 0),
            toolbar_visibility='no_menu_minimal',
        ), transition='in_scale', origin_widget=None)

        bui.textwidget(
            parent=self._root_widget, position=(self._width * 0.5, self._height - 45), size=(0, 0),
            text="Figure Player", scale=1.3, color=(0.4, 1.0, 0.6), h_align='center', v_align='center'
        )

        

        bui.textwidget(
            parent=self._root_widget, position=(self._width * 0.5, self._height * 0.5 + 45), size=(0, 0),
            text="Scan an existing profile, or create a new one",
            scale=0.9, color=(0.8, 0.8, 0.8), h_align='center', v_align='center'
        )

        self._scan_button = bui.buttonwidget(
            parent=self._root_widget, position=(self._width * 0.5 - 230, self._height * 0.5 - 30), size=(210, 50),
            label="Scan Figure Player", color=(0.2, 0.6, 1.0), on_activate_call=self._trigger_scan_sequence
        )

        self._create_button = bui.buttonwidget(
            parent=self._root_widget, position=(self._width * 0.5 + 20, self._height * 0.5 - 30), size=(210, 50),
            label="New Figure Player", color=(0.3, 0.8, 0.4), on_activate_call=self._trigger_creation_sequence
        )

        self._close_button = bui.buttonwidget(
            parent=self._root_widget, position=(self._width * 0.5 - 60, 20), size=(120, 38),
            label="Back", on_activate_call=self.back_to_menu
        )
        
        bui.buttonwidget(edit=self._scan_button, right_widget=self._create_button, down_widget=self._close_button)
        bui.buttonwidget(edit=self._create_button, left_widget=self._scan_button, down_widget=self._close_button)
        bui.buttonwidget(edit=self._close_button, up_widget=self._scan_button)

        bui.containerwidget(edit=self._root_widget, cancel_button=self._close_button, start_button=self._scan_button, selected_child=self._scan_button)

   
    def _trigger_scan_sequence(self):
        from .helpers import open_file_explorer_native
        open_file_explorer_native(self.on_scan)

    def _trigger_creation_sequence(self):
        FigureCreationWindow(origin_widget=self._create_button)

    def on_scan(self, data):
        if not data:
            return

        bs.get_foreground_host_activity().play_scan_entrance_cinematic(
            data
        )

        self._close()
     

    def back_to_menu(self):
        bui.app.classic.return_to_main_menu_session_gracefully(True)

    def _close(self):
        bui.containerwidget(edit=self._root_widget, transition='out_scale')

class FigureEditWindow(PopupWindow):
    
    def __init__(self, activity: FigureActivity):
        self._activity = activity
        self._data = activity.data_loaded

        self._width = 460.0
        self._height = 680.0
        # Original path
        mods_dir = bs.app.env.python_directory_user
        safe_name = "".join([c for c in self._data['nickname'] if c.isalnum()]).strip()
        if not safe_name:
            safe_name = "figure"       
        file_name = f"{safe_name}.figureplayer"
        self.original_path = os.path.join(mods_dir, file_name)

        super().__init__(
            position=(-400, -110),
            size=(self._width, self._height),
            bg_color=(0.12, 0.12, 0.16, 0.92)
        )

        bui.textwidget(
            parent=self.root_widget, position=(self._width * 0.5, self._height - 35), size=(0, 0),
            text="Editor", scale=1.4, color=(0.4, 0.9, 0.6), h_align='center', v_align='center'
        )

        bui.textwidget(
            parent=self.root_widget, text="Nickname:", position=(40, self._height - 95),
            size=(0, 0), h_align='left', v_align='center', scale=1.0, color=(0.8, 0.8, 0.8)
        )
        self._sve_button = bui.buttonwidget(
            parent=self.root_widget, position=(60, self._height-65), size=(100, 50),
            label="Save", color=(0.2, 0.7, 0.35), on_activate_call=self._trigger_save
        )
        self._text_field = bui.textwidget(
            parent=self.root_widget, position=(158, self._height - 115), size=(180, 37),
            text=self._data.get('nickname', 'Spaz'), h_align='left', v_align='center', editable=True, max_chars=14,
            color=(1.0, 1.0, 1.0), on_return_press_call=self._update_spaz_properties
        )

        fig_level = self._data.get('level', 1)
        bui.textwidget(
            parent=self.root_widget, text=f"LV. {fig_level}", position=(360, self._height - 95),
            size=(0, 0), h_align='left', v_align='center', scale=1.1, color=(1.0, 0.8, 0.2)
        )

        

        self._color_button = bui.buttonwidget(
            parent=self.root_widget, position=(40, self._height - 200), size=(170, 48),
            color=self._data['color'], label='Color',
            on_activate_call=lambda: self._make_picker('color', self._color_button.get_screen_space_center())
        )

        self._highlight_button = bui.buttonwidget(
            parent=self.root_widget, position=(250, self._height - 200), size=(170, 48),
            color=self._data['highlight'], label='Highlight',
            on_activate_call=lambda: self._make_picker('highlight', self._highlight_button.get_screen_space_center())
        )

        bui.textwidget(
            parent=self.root_widget, position=(self._width * 0.5, self._height - 245), size=(0, 0),
            text="Feed Abilities", scale=1.0, color=(0.7, 0.7, 0.7), h_align='center', v_align='center'
        )

        self._available_abilities = []
        for ability in ability_costs:
            self._available_abilities.append(ability)

        

        self._ability_menu = PopupMenu(
            parent=self.root_widget, position=(40, self._height - 310), width=240,
            choices=self._available_abilities, current_choice=self._available_abilities[0]
        )

        self._feed_button = bui.buttonwidget(
            parent=self.root_widget, position=(300, self._height - 306), size=(120, 44),
            label="Feed", color=(1.0, 0.55, 0.1), on_activate_call=self._feed_ability
        )

        bui.textwidget(
            parent=self.root_widget, position=(40, self._height - 355), size=(0, 0),
            text="Abilities (Click to remove):", scale=0.8, color=(0.5, 0.6, 0.7), h_align='left', v_align='center'
        )


        
        self._slot_buttons: list[bui.Widget] = []
        self._refresh_ability_slots()

        

        self._learning_enabled = self._data.get('learn', True)
        self._learning_button = bui.buttonwidget(
            parent=self.root_widget, 
            position=(100, self._height - 600), 
            size=(270, 42),
            label="Learning: ON" if self._learning_enabled else "Learning: OFF",
            color=(0.2, 0.6, 0.3) if self._learning_enabled else (0.4, 0.4, 0.45),
            on_activate_call=self._toggle_learning_mode
        )
        

        

        bui.containerwidget(edit=self.root_widget, start_button=self._sve_button, selected_child=self._text_field)
    
    def _toggle_learning_mode(self) -> None:
        self._learning_enabled = not self._learning_enabled
        self._data['learn'] = self._learning_enabled
        
        if self._learning_enabled:
            bui.buttonwidget(
                edit=self._learning_button, 
                label="Learning: ON", 
                color=(0.2, 0.6, 0.3)
            )
            bui.getsound('powerup01').play()
        else:
            bui.buttonwidget(
                edit=self._learning_button, 
                label="Learning: OFF", 
                color=(0.4, 0.4, 0.45)
            )
            bui.getsound('powerdown01').play()

    def _refresh_ability_slots(self) -> None:
        for btn in self._slot_buttons:
            if btn:
                btn.delete()
        self._slot_buttons.clear()

        

        start_y = self._height - 420
        base_height = 44.0
        gap = 10.0
        
        idx = 0
        abilities = self._data['abilities']
        num_slots = len(abilities)
        
        while idx < num_slots:
            ability = abilities[idx]
            
            slots_taken = 1
            if ability is not None:
                slots_taken = ability_costs.get(ability, 1)

         
            btn_height = (base_height * slots_taken) + (gap * (slots_taken - 1))
            pos_y = start_y - (idx * (base_height + gap)) - (btn_height - base_height)

            if ability is None:
                lbl = f"Empty"
                btn_color = (0.25, 0.25, 0.3)
            else:
                lbl = f"{ability}"

                btn_color = (0.2, 0.5, 0.8) if slots_taken == 1 else ((0.5, 0.3, 0.7) if slots_taken == 2 else (0.8, 0.3, 0.3))

            btn = bui.buttonwidget(
                parent=self.root_widget,
                position=(40, pos_y),
                size=(380, btn_height),
                label=lbl,
                color=btn_color,
                on_activate_call=bui.Call(self._clear_slot, idx)
            )
            self._slot_buttons.append(btn)
            
           

            idx += slots_taken

       
            
          

       

    def _feed_ability(self) -> None:
        chosen_ability = self._ability_menu._current_choice

        
        cost = ability_costs.get(chosen_ability, 1)
        abilities = self._data['abilities']
        num_slots = len(abilities)

   
        target_idx = -1
        for i in range(num_slots - cost + 1):
            if all(abilities[i + j] is None for j in range(cost)):
                target_idx = i
                break

        if target_idx == -1:
            bui.getsound('error').play()
            bs.screenmessage(f"Not enough empty slots ({cost} required)!", color=(1.0, 0.4, 0.4))
            return

        # multi eaten abilities gotta have smth riht?
        abilities[target_idx] = chosen_ability
        for j in range(1, cost):
            abilities[target_idx + j] = "Eaten"

        bui.getsound('amiibo/ability_gain' + str(
            random.randint(1, 2)
        )).play(0.25)
        if self._activity.actor and self._activity.actor.node:
            self._activity.actor.handlemessage(bs.CelebrateMessage(1.0))
            with bs.get_foreground_host_activity().context:
                bs.emitfx(position=self._activity.actor.node.position, velocity=(0, 1, 0), count=20,
                        chunk_type='spark', scale=2.5)
                
        self._refresh_ability_slots()

    def _clear_slot(self, index: int) -> None:
        abilities = self._data['abilities']
        ability = abilities[index]
        
        if ability is None or ability == "Eaten":
            return

       
        abilities[index] = None
        
        # kill "eaten"
        next_idx = index + 1
        while next_idx < len(abilities) and abilities[next_idx] == "Eaten":
            abilities[next_idx] = None
            next_idx += 1

        bui.getsound('block').play()
        self._refresh_ability_slots()

    
    def _make_picker(self, picker_type: str, origin: tuple[float, float]) -> None:
        ColorPicker(
            parent=self.root_widget, position=origin,
            offset=(-110 if picker_type == 'color' else 110, 0),
            initial_color=self._data['color'] if picker_type == 'color' else self._data['highlight'],
            delegate=self, tag=picker_type
        )

    def color_picker_selected_color(self, picker: ColorPicker, color: tuple[float, float, float]) -> None:
        if picker.get_tag() == 'color':
            self._data['color'] = color
            bui.buttonwidget(edit=self._color_button, color=color)
        else:
            self._data['highlight'] = color
            bui.buttonwidget(edit=self._highlight_button, color=color)
        self._update_spaz_properties()

    def color_picker_closing(self, *args) -> None:
        pass

    def _update_spaz_properties(self) -> None:
        name_query = bui.textwidget(query=self._text_field)
        if name_query and name_query.strip():
            self._data['nickname'] = name_query.strip()
            
        if self._activity.actor and self._activity.actor.node:
            self._activity.actor.node.name = self._data['nickname']
            self._activity.actor.node.name_color = self._data['color']
            self._activity.actor.node.color = self._data['color']
            self._activity.actor.node.highlight = self._data['highlight']

    def _trigger_save(self) -> None:
                        
                        mods_dir = bs.app.env.python_directory_user
                        safe_name = "".join([c for c in self._data['nickname'] if c.isalnum()]).strip()
                        if not safe_name:
                            safe_name = "figure"
                            
                        file_name = f"{safe_name}.figureplayer"
                        target_path = os.path.join(mods_dir, file_name)

                        
                        try:
                                json_str = json.dumps(self._data, indent=4)
                                json_bytes = json_str.encode('utf-8')
                                
                                compressed_bytes = zlib.compress(json_bytes)
                                
                                ciphered_bytes = _xor_cipher(compressed_bytes)
                                
                                final_b64_string = base64.b64encode(ciphered_bytes).decode('ascii')

                                with open(target_path, 'w', encoding='utf-8') as f:
                                    f.write(final_b64_string)
                                    
                                bui.getsound('gunCocking').play()
                                bs.screenmessage(f"Saved {self._data['nickname']} in Mods folder.", color=(0.3, 1, 0.5))
                              
                        except Exception as e:
                                print(f"[Figure Player] Figure Encryption Save Error: {e}")
                                bui.getsound('error').play()
                                bs.screenmessage("Svae failed. Check console.", color=(1, 0, 0))
                                
                        
                        if (os.path.exists(self.original_path)
                            and
                            self.original_path != target_path
                        ):
                            os.remove(self.original_path)
                        self._exit_editor()

        

    def _exit_editor(self) -> None:
        self._activity = None
        self._data = {}
        
        bui.containerwidget(edit=self.root_widget, transition='out_scale')
        bs.get_foreground_host_activity().reset()
        
        

class FigureActivity(bs.Activity[bs.Player, bs.Team]):
    """Activity showing the rotating main menu bg stuff."""

    _stdassets = bs.Dependency(bs.AssetPackage, 'stdassets@1')



    def __init__(self, settings: dict):
        super().__init__(settings)
        self.data_loaded = {}
        self.actor: Spaz = None
        

 
        

        
        
            
            
    def on_begin(self):
        super().on_begin()
        _babase.set_camera_manual(False)
        

        with bs.ContextRef.empty():
            bui.app.ui_v1.set_main_window(
                FigureManagerWindow(),
                is_top_level=False,
                suppress_warning=True,
                from_window=False,
            )

        
    
    def reset(self):
        self.set_music('main')
        
        if self.actor:
            self.actor.handlemessage(bs.DieMessage(immediate=True))
        self.data_loaded = {}
        _babase.set_camera_manual(False) 

        with bs.ContextRef.empty():
            bui.app.ui_v1.set_main_window(
                FigureManagerWindow(),
                is_top_level=True,
                suppress_warning=True,
                from_window=False,
            )
        
    def play_scan_entrance_cinematic(self, data) -> None:
        with self.context:

            _babase.set_camera_manual(True) ;_babase.set_camera_target(-0.5, 1, 0); _babase.set_camera_position(0, 2, 8)
            self.set_music('mute')
            bs.getsound('amiibo/scanned').play()
            assert bui.app.classic is not None
            appearance = bui.app.classic.spaz_appearances.get(data['character'])
            if not appearance:
                return

           
            char_tex = bs.gettexture(appearance.render)
            mask_tex = bs.gettexture(appearance.render_color_mask)
            bar_tex = bs.gettexture('bar')

            accent_color = (0.2, 0.9, 0.4)
            dark_bg = (0.05, 0.05, 0.08)

           
            top_bar = bs.newnode('image', attrs={
                'texture': bar_tex,
                'scale': (1500.0, 80.0),
                'color': accent_color,
                'opacity': 1.0,
            })
            bs.animate_array(top_bar, 'position', 2, {
                0.0: (0.0, 600.0), 
                0.4: (0.0, 220.0),
                2: (0.0, 225.0)
            })

            
            bottom_bar = bs.newnode('image', attrs={
                'texture': bar_tex,
                'scale': (1500.0, 180.0),
                'color': dark_bg,
                'opacity': 0.85,
            })
            bs.animate_array(bottom_bar, 'position', 2, {
                0.0: (0.0, -600.0), 
                0.4: (0.0, -180.0)
            })
            

            
            char_node = bs.newnode('image', attrs={
                'texture': char_tex,
                'tint_texture': mask_tex,
                'tint_color': data['color'],
                'tint2_color': data['highlight'],
                'scale': (1000.0, 1000.0),
            })
            bs.animate_array(char_node, 'position', 2, {
                0.1: (-600.0, -150.0), 
                0.5: (-220.0, -150.0),
                10: (-200.0, -150.0)
            })

            name_node = bs.newnode('text', attrs={
                'text': data['character'].upper(),
                'scale': 1.0,
                'color': (1.0, 1.0, 1.0),
                'h_align': 'center',
                'v_align': 'center',
                'flatness': 1.0,
                'big': True
            })
            bs.animate_array(name_node, 'position', 2, {
                0.1: (600.0, -180.0), 
                0.5: (180.0, -180.0),
                10: (160.0, -180.0)
            })

            fade_out_time = 2.0
            for node in (top_bar, bottom_bar, char_node, name_node):
                bs.animate(node, 'opacity', {
                    fade_out_time: node.opacity, 
                    fade_out_time + 0.5: 0.0
                })
                bs.timer(fade_out_time + 0.6, node.delete)
                
            
            self.data_loaded = data
            bs.timer(0.6 + fade_out_time + 0.1, self.show_editor)
    
    def show_editor(self):
        
        self.actor = Spaz(
            self.data_loaded['color'],self.data_loaded['highlight'],
            self.data_loaded['character'], None, False,
            False, False, False,
            self.data_loaded['cosmetic'],
        )
        self.actor.impact_scale = 0.0
        self.actor.handlemessage(bs.StandMessage((0, 3, 0)))
        self.actor.node.handlemessage('knockout', 2000)
        self.actor.node.name = self.data_loaded['nickname']
        self.actor.node.name_color = self.data_loaded['color']
        self.actor.node.hold_position_pressed = True
        self.actor.node.is_area_of_interest = False
        self.actor.node.move_up_down = -1
        bs.getsound('amiibo/spawned').play(0.25)
        bs.emitfx(position=self.actor.node.position, velocity=(0, -3, 0), count=12,
                    chunk_type='spark', scale=2.5)

        def cool():
            bs.getsound('amiibo/hi').play(0.25)
            bs.emitfx(position=self.actor.node.position, velocity=(0, 1, 0), count=20,
                    chunk_type='spark', scale=2.5)
            self.set_music('finalize')
            self.actor.node.handlemessage('attack_sound')
            self.actor.node.is_area_of_interest = True
            self.actor.handlemessage(bs.CelebrateMessage(0.5, 'right'))
            with bs.ContextRef.empty():
                FigureEditWindow(self)
                   
            
        bs.timer(2.5, cool)
    

    def set_music(self, type: str):
        max_volume = 4
        with self.context:

            if type == 'mute':
                self.main_theme.volume = 0
                self.create_new_theme.volume = 0
                self.finalize_theme.volume = 0
            
                

            elif type == 'main':
                if self.main_theme.volume != max_volume:

                    bs.animate(
                        self.main_theme, 'volume', {
                            0: 0,
                            0.25: max_volume
                        }
                    )
                if self.create_new_theme.volume != 0:
                    bs.animate(
                        self.create_new_theme, 'volume', {
                            0: max_volume,
                            1: 0
                        }
                    )
                if self.finalize_theme.volume != 0:
                    bs.animate(
                        self.finalize_theme, 'volume', {
                            0: max_volume,
                            1: 0
                        }
                    )
            elif type == 'create_new':
                if self.main_theme.volume != 0:

                    bs.animate(
                        self.main_theme, 'volume', {
                            0: 1,
                            1: 0
                        }
                    )
                if self.create_new_theme.volume != max_volume:
                    bs.animate(
                        self.create_new_theme, 'volume', {
                            0: 0,
                            0.75: max_volume
                        }
                    )
                if self.finalize_theme.volume != 0:
                    bs.animate(
                        self.finalize_theme, 'volume', {
                            0: max_volume,
                            1: 0
                        }
                    )
            elif type == 'finalize':
                if self.main_theme.volume != 0:

                    bs.animate(
                        self.main_theme, 'volume', {
                            0: max_volume,
                            1: 0
                        }
                    )
                if self.create_new_theme.volume != 0:
                    bs.animate(
                        self.create_new_theme, 'volume', {
                            0: max_volume,
                            1: 0
                        }
                    )
                if self.finalize_theme.volume != max_volume:
                    bs.animate(
                        self.finalize_theme, 'volume', {
                            0: 0,
                            0.25: max_volume
                        }
                    )
            

        
        
        
            
    

    
    @override
    def on_transition_in(self) -> None:
        # pylint: disable=too-many-locals
        # pylint: disable=too-many-statements
        super().on_transition_in()
        random.seed(123)
        app = bs.app
        env = app.env
        assert app.classic is not None

        plus = bs.app.plus
        assert plus is not None

        

    
        
            
        
       

    

        
       
        
        
        #trees_texture = bs.gettexture('treesColor')
        bgtex = bs.gettexture('white')
        bgmesh = bs.getmesh('thePadBG')
        color = (0.8, 0.8, 0.8)
        

        

        gnode = self.globalsnode
        gnode.tint = color
        gnode.ambient_color =color
        gnode.vignette_outer = color
        gnode.vignette_inner = color
        gnode.camera_mode = 'follow'
        
        self.collision = bs.Material()
        self.collision.add_actions(
            actions=(('modify_part_collision', 'collide', True)))

        
        # floor
            
        bs.newnode('region',
        attrs={'scale': (500.0, 1.0, 500.0),
                           'type': 'box',
                           'materials': [self.collision,
                                          SharedObjects.get().footing_material]})
   
        
       
        
        # music

        # MAIN THEME
       
        self.finalize_theme = bs.newnode('sound', attrs={
                'sound': bs.getsound('amiibo/makerFinalize'),
                'music': True,
                'volume': 0.0
            })
        def s():
            self.main_theme = bs.newnode('sound', attrs={
            'sound': bs.getsound('amiibo/makerMenu'),
            'music': True
          })

            self.create_new_theme = bs.newnode('sound', attrs={
                'sound': bs.getsound('amiibo/makerCreateNew'),
                'music': True,
                'volume': 0.0
            })
            self.set_music('main')
        bs.timer(0.25, s)
        self.bgterrain = bs.NodeActor(
            bs.newnode(
                'terrain',
                attrs={
                    'mesh': bgmesh,
                    'color':color,
                    'lighting': False,
                    'background': True,
                    'color_texture': bgtex,
                },
            )
        )

      



        


   
            
            
            
       
       

            




class FigureSession(bs.Session):
    """Session that runs the main menu environment."""

    def __init__(self) -> None:
        # Gather dependencies we'll need (just our activity).
        self._activity_deps = bs.DependencySet(bs.Dependency(FigureActivity))

        super().__init__([self._activity_deps])
        self._locked = False
        self.setactivity(bs.newactivity(FigureActivity))
        self.max_players = 0
        

        



    
        

    @override
    def on_activity_end(self, activity: bs.Activity, results: Any) -> None:
        if self._locked:
            bui.unlock_all_input()

        # Any ending activity leads us into the main menu one.
        self.setactivity(bs.newactivity(FigureActivity))


    @override
    def on_player_request(self, player: bs.SessionPlayer) -> bool:
        # Reject all player requests.
        return False
