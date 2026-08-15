"""UI for player's statistics."""
import bauiv1 as bui

class StatsWindow(bui.Window):
    """A popup window for showing stats in a vertical layout."""
    def __init__(
        self,
        transition: str = 'in_scale',
    ):
        uiscale = bui.app.ui_v1.uiscale
        self._width = (
            900 if uiscale is 
            bui.UIScale.SMALL else 500
        )
        self._height = (
            550 if uiscale is 
            bui.UIScale.SMALL else 350
        )
        scale = (
            1.55
            if uiscale is bui.UIScale.SMALL
            else 1.15 if uiscale is bui.UIScale.MEDIUM else 1.0
        )
        super().__init__(
            root_widget=bui.containerwidget(
                size=(self._width, self._height),
                scale=scale,
                transition=transition,
                toolbar_visibility='menu_minimal',
            ),
        )
        self._transitioning_out = False
        cfg = bui.app.config
        stats = [
            ('CRITICAL HITS:', 'GUMMY_statscrit', (0.2,1,0.2)),
            ('MINI CRITS:', 'GUMMY_statsminicrit', (1,1,0.2)),
            ('SHIELD BREAKS:', 'GUMMY_statsshieldbreaks', (0,1,1)),
            ('BOLTEDs:', 'GUMMY_statsbolteds', (1,1,1)),
            ('MINEXECUTIONs:', 'GUMMY_statsminexecutions', (1,0.5,0)),
            ("IMPULS'Ds:", 'GUMMY_statsimpulsd', (0.5,0.25,1)),
            ('GOLD STATUES:', 'GUMMY_statsgoldstatue', (1,1,0)),
            ('ANKLES BROKEN:', "GUMMY_statsbrokenankles", (0.8, 0.8, 0.8))
        ]
        y = self._height - 75
        bui.textwidget(
            parent=self._root_widget,
            position=(self._width * 0.5, self._height - (90 if uiscale is bui.UIScale.SMALL else 35)),
            size=(0, 0),
            text='Stats',
            color=bui.app.ui_v1.title_color,
            maxwidth=self._width * 0.8,
            h_align='center',
            v_align='center',
        )
        spacing = (
            100 if uiscale 
            is bui.UIScale.SMALL 
            else 80 if uiscale
            is bui.UIScale.MEDIUM
            else 60
        )
        if uiscale is bui.UIScale.SMALL:
            y -= 90
        for label, key, color in stats:
            bui.textwidget(
                parent=self._root_widget,
                position=(spacing - 10, y),
                size=(0, 0),
                text=label,
                color=color,
                h_align='left',
                v_align='center',
                maxwidth=180,
                scale=0.95,
            )
            bui.textwidget(
                parent=self._root_widget,
                position=(self._width - spacing, y),
                size=(0, 0),
                text=str(cfg.get(key, 0)),
                color=(1, 1, 1),
                h_align='right',
                v_align='center',
                maxwidth=70,
                scale=0.95,
            )
            y -= 30
        if uiscale is bui.UIScale.SMALL:
            bui.containerwidget(
                edit=self._root_widget, 
                on_cancel_call=self._on_cancel_press,
            )
        else:
            self._cancel_button = bui.buttonwidget(
                parent=self._root_widget,
                position=(25, self._height - 53),
                size=(50, 50),
                scale=0.8,
                label=bui.charstr(bui.SpecialChar.PLAY_STATION_CROSS_BUTTON),
                on_activate_call=self._on_cancel_press,
                autoselect=True,
                text_scale=1.2,
            )
            bui.containerwidget(
                edit=self._root_widget,
                cancel_button=self._cancel_button,
            )
        
    def _on_cancel_press(self):
        self._transition_out()
       
    def _transition_out(self) -> None:
        if not self._transitioning_out:
            self._transitioning_out = True
            bui.containerwidget(
                edit=self._root_widget, 
                transition='out_scale',
            )