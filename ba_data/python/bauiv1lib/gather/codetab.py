# Released under the MIT License. See LICENSE for details.
#
"""Defines the code tab in the gather UI."""
# pylint: disable=too-many-lines

from __future__ import annotations

import logging
import base64
from enum import Enum
from threading import Thread
from dataclasses import dataclass
from typing import TYPE_CHECKING, cast, override
from bauiv1lib.gather import GatherTab
import babase


import bauiv1 as bui
import bascenev1 as bs

if TYPE_CHECKING:
    from typing import Any, Callable

    from bauiv1lib.gather import GatherWindow


def _encode_party_code(ip: str, port: int) -> str:
    XOR_KEY = 73 # el key
    raw_str = f"{ip}|{port}"
    
    xor_bytes = bytes([ord(c) ^ XOR_KEY for c in raw_str])
    encoded = base64.b32encode(xor_bytes).decode('utf-8').replace('=', '')
    return encoded


def _decode_party_code(code: str) -> tuple[str, int, str] | None:
    XOR_KEY = 73
    try:
        code = code.upper().strip()
        missing_padding = len(code) % 8
        if missing_padding:
            code += '=' * (8 - missing_padding)
            
        xor_bytes = base64.b32decode(code.encode('utf-8'))
        decoded_bytes = bytes([b ^ XOR_KEY for b in xor_bytes])
        decoded_str = decoded_bytes.decode('utf-8')
        
        ip, port_str = decoded_str.split('|')
        return ip, int(port_str)
    except Exception:
        return None


class _HostLookupThread(Thread):
    """Thread to fetch an addr."""

    def __init__(
        self, name: str, port: int, call: Callable[[str | None, int], Any]
    ):
        super().__init__()
        self._name = name
        self._port = port
        self._call = call

    @override
    def run(self) -> None:
        result: str | None
        try:
            import socket

            aresult = [
                item[-1][0]
                for item in socket.getaddrinfo(self._name, self._port)
            ][0]
            if isinstance(aresult, int):
                raise RuntimeError('Unexpected getaddrinfo int result')
            result = aresult
        except Exception:
            result = None
        bui.pushcall(
            lambda: self._call(result, self._port), from_other_thread=True
        )


class SubTabType(Enum):
    """Available sub-tabs."""

    JOIN_BY_CODE = 'join_by_code'


@dataclass
class State:
    """State saved/restored only while the app is running."""

    sub_tab: SubTabType = SubTabType.JOIN_BY_CODE


class CodeGatherTab(GatherTab):

    def __init__(self, window: GatherWindow) -> None:
        super().__init__(window)
        self._check_button: bui.Widget | None = None
        self._doing_access_check: bool | None = None
        self._access_check_count: int | None = None
        self._sub_tab: SubTabType = SubTabType.JOIN_BY_CODE
        self._t_addr: bui.Widget | None = None
        self._t_accessible: bui.Widget | None = None
        self._t_accessible_extra: bui.Widget | None = None
        self._access_check_timer: bui.AppTimer | None = None
        self._checking_state_text: bui.Widget | None = None
        self._container: bui.Widget | None = None
        self._width: float | None = None
        self._height: float | None = None
        self._scroll_width: float | None = None
        self._scroll_height: float | None = None
        self._scrollwidget: bui.Widget | None = None
        self._columnwidget: bui.Widget | None = None
        self._party_edit_name_text: bui.Widget | None = None
        self._party_edit_addr_text: bui.Widget | None = None
        self._party_edit_port_text: bui.Widget | None = None
        self._no_parties_added_text: bui.Widget | None = None
        self._copy_button = None
        self.ip_from_internet = None
        #  check if we hosted before, likey we are on the same IP so just use the same code
        if babase.app.config.get('GUMMY_last_code', ''):
            bs.app.host_code = babase.app.config['GUMMY_last_code']
            bs.app.is_hosting_code = True
        

    @override
    def on_activate(
        self,
        parent_widget: bui.Widget,
        tab_button: bui.Widget,
        region_width: float,
        region_height: float,
        region_left: float,
        region_bottom: float,
    ) -> bui.Widget:
        c_width = region_width
        c_height = region_height - 20

        self._container = bui.containerwidget(
            parent=parent_widget,
            position=(
                region_left,
                region_bottom + (region_height - c_height) * 0.5,
            ),
            size=(c_width, c_height),
            background=False,
            selection_loops_to_parent=True,
        )
        v = c_height - 30
        
        self._set_sub_tab(self._sub_tab, region_width, region_height)

        return self._container

    @override
    def save_state(self) -> None:
        return

    @override
    def restore_state(self) -> None:
        assert bui.app.classic is not None
        state = bui.app.ui_v1.window_states.get(type(self))
        if state is None:
            state = State()
        assert isinstance(state, State)
        self._sub_tab = state.sub_tab

    def _set_sub_tab(
        self,
        value: SubTabType,
        region_width: float,
        region_height: float,
        playsound: bool = False,
    ) -> None:
        assert self._container
        if playsound:
            bui.getsound('click01').play()
        
        for widget in self._container.get_children():
           
            widget.delete()

        self._build_join_by_code_tab(region_width, region_height)

    def _build_join_by_code_tab(
        self, region_width: float, region_height: float
    ) -> None:
        c_width = region_width
        c_height = region_height - 20
        v = c_height - 95
        
      
        bui.textwidget(
            parent=self._container,
            position=(c_width * 0.5, v + 75),
            color=(0.5, 0.6, 0.7),
            scale=0.75,
            size=(0, 0),
            h_align='center',
            v_align='center',
            text="Are you tired of setting ips every time your friends host? Use this tool to make it faster to join games :D",
        )

        bui.textwidget(
            parent=self._container,
            position=(c_width * 0.5, v + 40),
            color=(0.3, 0.8, 1.0),
            scale=1.1,
            size=(0, 0),
            h_align='center',
            v_align='center',
            text="Party Code",
        )
        
        code_input = bui.textwidget(
            parent=self._container,
            editable=True,
            position=(c_width * 0.5 - 200, v - 35),
            text=babase.app.config.get('GUMMY_last_code_used', ''),
            autoselect=True,
            v_align='center',
            h_align='center',
            scale=1.2,
            maxwidth=380,
            size=(400, 45),
        )
        
        code_btn = bui.buttonwidget(
            parent=self._container,
            size=(240, 50),
            color=(0.2, 0.6, 0.8),
            label="Join Party",
            position=(c_width * 0.5 - 120, v - 100),
            autoselect=True,
            on_activate_call=bui.Call(self._connect_via_code, code_input),
        )

        bui.widget(edit=code_input, down_widget=code_btn)
        bui.textwidget(edit=code_input, on_return_press_call=code_btn.activate)
        
        v -= 185
        scl = 1.5
     
        if bs.app.is_hosting_code:
            def bruh():
                self._stop_hosting_action(region_width,region_height)
                self._on_show_my_address_button_press(v, self._container, c_width)
            self._check_button = bui.buttonwidget(
                parent=self._container,
                size=(320*scl, (48*scl)+20),
                label=f"Host code:\n{bs.app.host_code}\nClick for a new code",
                color=(0.7, 0.2, 0.2),
                position=(c_width * 0.5 - 160*scl, v),
                autoselect=True,
                on_activate_call=bui.Call(bruh),
            )
            if babase.clipboard_is_supported():
                def copy():
                    babase.clipboard_set_text(bs.app.host_code)
                    bui.screenmessage("Code copied to clipboard!", color=(0.2, 1.0, 0.5))
                    bui.getsound('gunCocking').play()
                self._copy_button = bui.buttonwidget(
                    parent=self._container,
                    size=(210*scl, 20*scl),
                    label=f"Copy Code",
                    position=(c_width * 0.5 - 100*scl, v-40),
                    autoselect=True,
                    on_activate_call=bui.Call(copy),
                )
        else:
            self._check_button = bui.buttonwidget(
                parent=self._container,
                size=(320*scl, 48*scl),
                label="Get code",
                color=(0.15, 0.6, 0.15),
                position=(c_width * 0.5 - 160*scl, v),
                autoselect=True,
                on_activate_call=bui.Call(
                    self._on_show_my_address_button_press,
                    v,
                    self._container,
                    c_width,
                ),
            )
        bui.widget(edit=self._check_button, up_widget=code_btn)

    def _stop_hosting_action(self, r_w: float, r_h: float) -> None:
        bs.app.is_hosting_code = False
        bs.app.host_code = ''
        babase.app.config['GUMMY_last_code'] = ''
        bui.getsound('shieldDown').play()

    def _connect_via_code(self, code_widget: bui.Widget) -> None:
        code_str = cast(str, bui.textwidget(query=code_widget))
        if not code_str:
            bui.screenmessage("Error: invalid address.", color=(1, 0, 0))
            bui.getsound('error').play()
            return
            
        decoded = _decode_party_code(code_str)
        if decoded is None:
            bui.screenmessage("Error: invalid address.", color=(1, 0, 0))
            bui.getsound('error').play()
            return
            
        ip, port = decoded
        
        def result(
        resolved_address: str | None, res_port: int
        ):
            bs.connect_to_party(resolved_address, port=res_port)
        _HostLookupThread(
                name=ip,
                port=port,
                call=bui.WeakCall(result),
            ).start()
        babase.app.config['GUMMY_last_code_used'] = code_str
        babase.app.config.apply_and_commit()


    
    @override
    def on_deactivate(self) -> None:
        self._access_check_timer = None



    def _on_show_my_address_button_press(
        self, v2: float, container: bui.Widget | None, c_width: float
    ) -> None:
        if not container:
            return

        bui.getsound('swish').play()
        v2 -= 20 
        
        self._checking_state_text = bui.textwidget(
            parent=container,
            position=(c_width * 0.5, v2),
            color=(0.8, 0.8, 0.8),
            scale=0.95,
            size=(0, 0),
            maxwidth=c_width * 0.9,
            h_align='center',
            v_align='center',
            text="Loading...",
        )

        self._doing_access_check = False
        self._access_check_count = 0
        self._access_check_timer = bui.AppTimer(
            10.0,
            bui.WeakCall(
                self._access_check_update,
                self._checking_state_text,
                self._checking_state_text,
                self._checking_state_text,
            ),
            repeat=True,
        )

        self._access_check_update(self._checking_state_text, self._checking_state_text, self._checking_state_text)
        if self._check_button:
            self._check_button.delete()
        if self._copy_button:
            self._copy_button .delete()

    def _access_check_update(
        self,
        t_addr: bui.Widget,
        t_accessible: bui.Widget,
        t_accessible_extra: bui.Widget,
    ) -> None:
        assert bui.app.classic is not None
        assert self._doing_access_check is not None
        assert self._access_check_count is not None
        if not self._doing_access_check and self._access_check_count < 100:
            self._doing_access_check = True
            self._access_check_count += 1
            self._t_addr = t_addr
            self._t_accessible = t_accessible
            self._t_accessible_extra = t_accessible_extra
            bui.app.classic.master_server_v1_get(
                'bsAccessCheck',
                {'b': bui.app.env.engine_build_number},
                callback=bui.WeakCall(self._on_accessible_response),
            )

    def _on_accessible_response(self, data: dict[str, Any] | None) -> None:
        self._doing_access_check = False
        if not self._checking_state_text or not self._container:
            return

        if data is None or 'address' not in data or 'accessible' not in data:
            bui.textwidget(
                edit=self._checking_state_text,
                text="Check your wifi connection and try again.",
                color=(1, 1, 0),
            )
            return
        
        # Safely fetch container width using the class attribute or fallback to a standard layout width
        # (Gather tabs are usually around 800-1000 width depending on the parent window)
        c_width = 850.0 
        
        if data['accessible']:
            self.ip_from_internet = data['address']
           
            
            party_code = _encode_party_code(
                ip=self.ip_from_internet,
                port=bs.get_game_port(),
            )
            
            bui.screenmessage(f"Refresh the tab to get your code...", color=(0.2, 1.0, 0.5))
            bs.app.is_hosting_code = True
            bs.app.host_code = party_code
            babase.app.config['GUMMY_last_code'] = party_code
            babase.app.config.apply_and_commit()
            
        else:
            self.ip_from_internet = None
            bs.app.is_hosting_code = False
            bs.app.host_code = ''
            babase.app.config['GUMMY_last_code'] = ''
            
            
            pos_y = 190.0
            
            bui.textwidget(edit=self._checking_state_text, text="")
            
            bui.textwidget(
                parent=self._container,
                position=(c_width * 0.5, pos_y),
                text=f"Your port {bs.get_game_port()} is not UDP forwarded.\nIf you're using external apps to host, enter them below!",
                color=(1, 0.4, 0.2),
                scale=0.75,
                size=(0, 0),
                h_align='center',
                v_align='center',
                maxwidth=c_width * 0.9
            )
            
            # Step down cleanly for the manual input layout row
            pos_y -= 45
            
            # IP Input Setup
            bui.textwidget(
                parent=self._container,
                position=(c_width * 0.5 - 195, pos_y),
                text="IP:",
                color=(0.6, 0.8, 1.0),
                scale=0.8,
                size=(0, 0),
                h_align='right',
                v_align='center'
            )
            manual_ip = bui.textwidget(
                parent=self._container,
                editable=True,
                position=(c_width * 0.5 - 185, pos_y - 17.5),
                size=(180, 35),
                text="",
                v_align='center',
                scale=0.95,
            )
            
            bui.textwidget(
                parent=self._container,
                position=(c_width * 0.5 + 35, pos_y),
                text="Port:",
                color=(0.6, 0.8, 1.0),
                scale=0.8,
                size=(0, 0),
                h_align='right',
                v_align='center'
            )
            manual_port = bui.textwidget(
                parent=self._container,
                editable=True,
                position=(c_width * 0.5 + 45, pos_y - 17.5),
                size=(85, 35),
                text=str(bs.get_game_port()),
                v_align='center',
                scale=0.95,
            )
            
        
            build_code_btn = bui.buttonwidget(
                parent=self._container,
                position=(c_width * 0.5 + 140, pos_y - 17.5),
                size=(110, 35),
                label="Make Code",
                color=(0.3, 0.5, 0.7),
                on_activate_call=bui.Call(self._compile_manual_code, manual_ip, manual_port),
            )
            
            self._access_check_timer = None

    def _compile_manual_code(self, ip_widget: bui.Widget, port_widget: bui.Widget) -> None:
        ip_str = cast(str, bui.textwidget(query=ip_widget)).strip()
        port_str = cast(str, bui.textwidget(query=port_widget)).strip()
        
        if not ip_str or not port_str:
            bui.screenmessage("Son", color=(1, 0, 0))
            bui.getsound('error').play()
            return
            
        try:
            port_val = int(port_str)
        except ValueError:
            bui.screenmessage("Port is not annumber", color=(1, 0, 0))
            bui.getsound('error').play()
            return
            

        compiled_token = _encode_party_code(ip=ip_str, port=port_val)
        
        # Display built token on a structural overlay modal popup message
        bui.getsound('gunCocking').play()
        bui.screenmessage(f"Join code: {compiled_token}", color=(0.2, 1.0, 0.5))
        bs.app.is_hosting_code = True
        bs.app.host_code = compiled_token
        babase.app.config['GUMMY_last_code'] = compiled_token
        babase.app.config.apply_and_commit()
        bui.screenmessage(f"Refresh the tab to get your code...", color=(0.2, 1.0, 0.5))
      
            