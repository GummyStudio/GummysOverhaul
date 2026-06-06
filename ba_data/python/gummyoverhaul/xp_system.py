import bascenev1 as bs
import bauiv1 as bui

class XP:
    def __init__(self):
        super().__init__()
        self.xp_per_level = 15
        cfg = bs.app.config
        self.max_level = cfg.get('GUMMY_max_level', 200)

    def award_xp(self, amount: int, show_in_game: bool = False, position: tuple = (0, 0, 0), scrnmessage: bool = False):
        cfg = bs.app.config 
        current_xp = cfg.get('GUMMY_xp', 0)
        current_level = cfg.get('GUMMY_level', 1)

        old_level = current_level

        new_xp = current_xp + amount

        xp_required = self.xp_per_level + ((current_level - 1) * 10)

        # Level‑up logic
        while new_xp >= xp_required and current_level < self.max_level:
            new_xp -= xp_required
            current_level += 1
            xp_required = self.xp_per_level + ((current_level - 1) * 10)

        if current_level > old_level:
            self._show_levelup(old_level, current_level)

        cfg['GUMMY_xp'] = new_xp
        cfg['GUMMY_level'] = current_level
        cfg['GUMMY_max_level'] = self.max_level
        

        if show_in_game:

            if scrnmessage:
                bs.screenmessage(f'+{amount} XP', color=(1, 0.8, 0.7))


            if position is not None and not cfg['remove_xp_stuff_lomao']:
                from bascenev1lib.actor.popuptext import PopupText
                try:
                    if not isinstance(bs.getactivity(), bs.GameActivity):
                        return

                        
                    d = PopupText(
                                f'+{amount} XP',
                                position=position,
                                color=(1, 0.8, 0.7),
                                random_offset=0.65,
                                scale=0.67
                    ).autoretain()
                    d.node.host_only = True
                    d = None

                    d2 = PopupText(
                                f'+{amount} XP',
                                position=position,
                                color=(1, 0, 0),
                                random_offset=0.65,
                                scale=0.67
                    ).autoretain()
                    d2.node.client_only = True
                    d2 = None
                    
                except bs.ActivityNotFoundError:
                    pass

        cfg.apply_and_commit()

    def get_xp_and_level(self):
        cfg = bs.app.config
        return cfg.get('GUMMY_xp', 0), cfg.get('GUMMY_level', 1)

    def _show_levelup(self, old_level: int, new_level: int):
        
        try:
            bs.getsound('levelup').play(0.76)
           
            

            # Create a text node
            duration = 3
            txt = bs.newnode('text',
                attrs={
                    'text': f"LEVEL UP! {old_level} -> {new_level}",
                    'h_align': 'right',
                    'v_align': 'center',
                    'h_attach': 'right',
                    'v_attach': 'bottom',
                    'scale': 1,
                    'color': (1, 1, 0, 1),  # yellow with full alpha
                    'shadow': 1.0,
                    'host_only': True
                }
            )

            # Animate position: float up
            start_y = 100
            end_y = 160
            bs.animate_array(txt, 'position', 2, {0.0: (0, start_y), 0.5: (0, end_y)})

            # Animate opacity: fade out
            bs.animate(txt, 'opacity', {1.0: 1.0, duration: 0.0})

            # Remove the node after duration
            bs.timer(duration, txt.delete)

            # Create one for clients
            txt = bs.newnode('text',
                attrs={
                    'text': f"{bs.app.plus.get_v1_account_display_string()} LEVELED UP! ({old_level} -> {new_level})",
                    'h_align': 'right',
                    'v_align': 'center',
                    'h_attach': 'right',
                    'v_attach': 'bottom',
                    'scale': 0.6,
                    'color': (1, 1, 0, 1), 
                    'shadow': 1.0,
                    'client_only': True
                }
            )

            # Animate position: float up
            start_y = 100
            end_y = 160
            bs.animate_array(txt, 'position', 2, {0.0: (0, start_y), 0.5: (0, end_y)})

            # Animate opacity: fade out
            bs.animate(txt, 'opacity', {1.0: 1.0, duration: 0.0})

            # Remove the node after duration
            bs.timer(duration, txt.delete)
        except bs.ContextError:
            # Okay... lets just show it to our host with a screenemssage.
            bui.getsound('levelup').play(0.76)
            bui.screenmessage(f"LEVEL UP! {old_level} -> {new_level}", color=(1, 0.8, 0.7))
        cfg = bui.app.config
        ach = bui.app.classic.ach
        if cfg['GUMMY_level'] > 25:
            ach.award_local_achievement('Milestone1')
        if cfg['GUMMY_level'] > 50:
            ach.award_local_achievement('Milestone2')
        if cfg['GUMMY_level'] > 75:
            ach.award_local_achievement('Milestone3')
        if cfg['GUMMY_level'] > 100:
            ach.award_local_achievement('Milestone4')
        if cfg['GUMMY_level'] > 199:
            ach.award_local_achievement('Milestone5')