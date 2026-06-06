# Released under the MIT License. See LICENSE for details.
#
"""Provides plus app subsystem."""
from __future__ import annotations

from typing import TYPE_CHECKING, override

from babase import AppSubsystem

import _baplus

if TYPE_CHECKING:
    from typing import Callable, Any

    import bacommon.bs
    from babase import AccountV2Subsystem

    from baplus._cloud import CloudSubsystem


class PlusAppSubsystem(AppSubsystem):
    """Subsystem for plus functionality in the app.

    Access the single shared instance of this class via the
    :attr:`~babase.App.plus` attr on the :class:`~babase.App` class.
    Note that it is possible for this to be ``None`` if the plus package
    is not present, so code should handle that case gracefully.
    """

    # pylint: disable=too-many-public-methods

    # Note: this is basically just a wrapper around _baplus for
    # type-checking purposes. Maybe there's some smart way we could skip
    # the overhead of this wrapper at runtime.

    accounts: AccountV2Subsystem
    cloud: CloudSubsystem

    @override
    def on_app_loading(self) -> None:
        """:meta private:"""
        _baplus.on_app_loading()
        self.accounts.on_app_loading()
        from gummyoverhaul.startup import GummysOverhaulStartUp

        self.startup = GummysOverhaulStartUp()
        # Setup an xp system
        from gummyoverhaul.xp_system import XP
        self.xp_sys = XP()

    @staticmethod
    def add_v1_account_transaction(
        transaction: dict, callback: Callable | None = None
    ) -> None:
        """:meta private:"""
        return _baplus.add_v1_account_transaction(transaction, callback)

    @staticmethod
    def game_service_has_leaderboard(game: str, config: str) -> bool:
        """Given a game and config string, returns whether there is a
        leaderboard for it on the game service.

        :meta private:
        """
        return _baplus.game_service_has_leaderboard(game, config)

    @staticmethod
    def get_master_server_address(source: int = -1, version: int = 1) -> str:
        """Return the address of the master server.

        :meta private:
        """
        return _baplus.get_master_server_address(source, version)

    @staticmethod
    def get_classic_news_show() -> str:
        """:meta private:"""
        return _baplus.get_classic_news_show()

    @staticmethod
    def get_price(item: str) -> str | None:
        """:meta private:"""
        return _baplus.get_price(item)

    @staticmethod
    def get_v1_account_product_purchased(item: str) -> bool:
        """:meta private:"""
        return _baplus.get_v1_account_product_purchased(item)

    @staticmethod
    def get_v1_account_product_purchases_state() -> int:
        """:meta private:"""
        return _baplus.get_v1_account_product_purchases_state()

    @staticmethod
    def get_v1_account_display_string(full: bool = True, true: bool = False) -> str:
        """:meta private:"""

        import babase
        user = _baplus.get_v1_account_display_string(full)
        return user

        if true:
            return user

        if 'GummyBoiYT' in user:
            user = 'gummuers'
            if full:
                user = babase.charstr(babase.SpecialChar.V2_LOGO) + user
        elif 'Buddie' in user:
            user = 'budbudbud'
            if full:
                user = babase.charstr(babase.SpecialChar.V2_LOGO) + user
        elif 'Mell' in user or 'MellBoi' in user or 'mell' in user:
            user = 'meg family guy'
            if full:
                user = babase.charstr(babase.SpecialChar.V2_LOGO) + user
        elif 'ggMustaGD' in user or 'ggMustaGD1' in user or 'ggMustaGD01' in user:
            user = 'muystarsd'
            if full:
                user = babase.charstr(babase.SpecialChar.V2_LOGO) + user
        elif 'SoK05' in user:
            user = 'sock'
            if full:
                user = babase.charstr(babase.SpecialChar.V2_LOGO) + user
        elif 'Achs' in user or 'AchsIdeas' in user:
            user = 'NinjaTurtle'
            if full:
                user = babase.charstr(babase.SpecialChar.V2_LOGO) + user
        elif 'LuceGangre' in user:
            user =  'lucye.,,,,'
            if full:
                user = babase.charstr(babase.SpecialChar.V2_LOGO) + user
        elif 'Gmod' in user or 'NoName12369' in user:
            user = 'sour lemon'
            if full:
                user = babase.charstr(babase.SpecialChar.V2_LOGO) + user
        
   
        return user
    

        

    @staticmethod
    def get_v1_account_misc_read_val(name: str, default_value: Any) -> Any:
        """:meta private:"""
        # um.. this is just that i dont have to go through pain manually adding the prices into the function.

        if name == 'price.characters.agentspaz':
            return 5600
        elif name == 'price.characters.amar':
            return 7800
        elif name == 'price.characters.bob':
            return 12530
        elif name == 'price.characters.watory':
            return 50000
        elif name == 'price.characters.space':
            return 500
        elif name == 'price.games.infinite_gummy_o':
            return 100
        elif name == 'price.games.infinite_gummy_r':
            return 3000
        elif name == 'price.games.tower':
            return 5000
        elif name == 'price.characters.vr':
            return 5600
        elif name == 'price.characters.pizza':
            return 1000
        elif name == 'price.characters.noise':
            return 1200
        elif name == 'price.characters.fbunny':
            return 10500
        elif name == 'price.characters.orangecap':
            return 500
        elif name == 'price.characters.ralsei':
            return 1200
        elif name == 'price.characters.betty':
            return 4500 # Originaly 350 but sok got mad at me :<
        elif name == 'price.characters.ire':
            return 2300
        elif name == 'price.characters.rem':
            return 1000
        elif name == 'price.characters.fennekin':
            return 5800
       
        

    
        
        # These use gumdollars.
        elif name == 'price.characters.spazexe':
            return 1
        elif name == 'price.characters.starhoodie':
            return 1
        elif name == 'price.characters.insane':
            return 3
        elif name == 'price.characters.bluecap':
            return 2
        elif name == 'price.characters.ninjaling':
            return 4
        elif name == 'price.characters.spazling':
            return 4
        elif name == 'price.characters.melling':
            return 4
        elif name == 'price.characters.sal':
            return 2
        elif name == 'price.characters.scoldy':
            return 6
        elif name == 'price.characters.hhh':
            return 1
        elif name == 'price.characters.jolly':
            return 3
        elif name == 'price.characters.gummyvoicespaz':
            return 3
        elif name == 'price.characters.gummyvoicejack':
            return 3
        elif name == 'price.characters.gummyvoiceagent':
            return 3
        elif name == 'price.characters.ybs16':
            return 3
        elif name == 'price.characters.tophat':
            return 4
        

            
        else:
            return _baplus.get_v1_account_misc_read_val(name, default_value)
    
    @staticmethod
    def get_gummysoverhaul_server_url():
        """ returns my server, this should not be touched, it'll break lotsa shet""" 
        return "https://gummys-overhaul-default-rtdb.firebaseio.com"

    @staticmethod
    def get_v1_account_misc_read_val_2(name: str, default_value: Any) -> Any:
        """:meta private:"""
        return _baplus.get_v1_account_misc_read_val_2(name, default_value)

    @staticmethod
    def get_v1_account_misc_val(name: str, default_value: Any) -> Any:
        """:meta private:"""
        return _baplus.get_v1_account_misc_val(name, default_value)

    @staticmethod
    def get_v1_account_name() -> str:
        """:meta private:"""
        return _baplus.get_v1_account_name()

    @staticmethod
    def get_v1_account_public_login_id() -> str | None:
        """:meta private:"""
        return _baplus.get_v1_account_public_login_id()

    @staticmethod
    def get_v1_account_state() -> str:
        """:meta private:"""
        return _baplus.get_v1_account_state()

    @staticmethod
    def get_v1_account_state_num() -> int:
        """:meta private:"""
        return _baplus.get_v1_account_state_num()

    @staticmethod
    def get_v1_account_ticket_count() -> int:
        """Return the number of tickets for the current account.

        :meta private:
        """
        return _baplus.get_v1_account_ticket_count()

    @staticmethod
    def get_v1_account_type() -> str:
        """:meta private:"""
        return _baplus.get_v1_account_type()

    @staticmethod
    def get_v2_fleet() -> str:
        """:meta private:"""
        return _baplus.get_v2_fleet()

    @staticmethod
    def have_outstanding_v1_account_transactions() -> bool:
        """:meta private:"""
        return _baplus.have_outstanding_v1_account_transactions()

    @staticmethod
    def in_game_purchase(item: str, price: int) -> None:
        """:meta private:"""
        return _baplus.in_game_purchase(item, price)

    @staticmethod
    def is_blessed() -> bool:
        """:meta private:"""
        return _baplus.is_blessed()

    @staticmethod
    def mark_config_dirty() -> None:
        """:meta private:"""
        return _baplus.mark_config_dirty()

    @staticmethod
    def power_ranking_query(callback: Callable, season: Any = None) -> None:
        """:meta private:"""
        return _baplus.power_ranking_query(callback, season)

    @staticmethod
    def purchase(item: str) -> None:
        """:meta private:"""
        return _baplus.purchase(item)

    @staticmethod
    def report_achievement(
        achievement: str, pass_to_account: bool = True
    ) -> None:
        """:meta private:"""
        return _baplus.report_achievement(achievement, pass_to_account)

    @staticmethod
    def reset_achievements() -> None:
        """:meta private:"""
        return _baplus.reset_achievements()

    @staticmethod
    def restore_purchases() -> None:
        """:meta private:"""
        return _baplus.restore_purchases()

    @staticmethod
    def run_v1_account_transactions() -> None:
        """:meta private:"""
        return _baplus.run_v1_account_transactions()

    @staticmethod
    def sign_in_v1(account_type: str) -> None:
        """:meta private:"""
        return _baplus.sign_in_v1(account_type)

    @staticmethod
    def sign_out_v1(v2_embedded: bool = False) -> None:
        """:meta private:"""
        return _baplus.sign_out_v1(v2_embedded)

    @staticmethod
    def submit_score(
        game: str,
        config: str,
        name: Any,
        score: int | None,
        callback: Callable,
        *,
        order: str = 'increasing',
        tournament_id: str | None = None,
        score_type: str = 'points',
        campaign: str | None = None,
        level: str | None = None,
    ) -> None:
        """Submit a score to the server.

        Callback will be called with the results. As a courtesy, please
        don't send fake scores to the server. I'd prefer to devote my
        time to improving the game instead of trying to make the score
        server more mischief-proof.

        :meta private:
        """
        return _baplus.submit_score(
            game,
            config,
            name,
            score,
            callback,
            order,
            tournament_id,
            score_type,
            campaign,
            level,
        )

    @staticmethod
    def tournament_query(
        callback: Callable[[dict | None], None], args: dict
    ) -> None:
        """:meta private:"""
        return _baplus.tournament_query(callback, args)

    @staticmethod
    def supports_purchases() -> bool:
        """Does this platform support in-app-purchases?

        :meta private:
        """
        return _baplus.supports_purchases()

    @staticmethod
    def have_incentivized_ad() -> bool:
        """Is an incentivized ad available?

        :meta private:
        """
        return _baplus.have_incentivized_ad()

    @staticmethod
    def has_video_ads() -> bool:
        """Are video ads available?

        :meta private:
        """
        return _baplus.has_video_ads()

    @staticmethod
    def can_show_ad() -> bool:
        """Can we show an ad?

        :meta private:
        """
        return _baplus.can_show_ad()

    @staticmethod
    def show_ad(
        purpose: str, on_completion_call: Callable[[], None] | None = None
    ) -> None:
        """Show an ad.

        :meta private:
        """
        _baplus.show_ad(purpose, on_completion_call)

    @staticmethod
    def show_ad_2(
        purpose: str, on_completion_call: Callable[[bool], None] | None = None
    ) -> None:
        """Show an ad.

        :meta private:
        """
        _baplus.show_ad_2(purpose, on_completion_call)

    @staticmethod
    def show_game_service_ui(
        show: str = 'general',
        game: str | None = None,
        game_version: str | None = None,
    ) -> None:
        """Show game-service provided UI.

        :meta private:
        """
        _baplus.show_game_service_ui(show, game, game_version)
