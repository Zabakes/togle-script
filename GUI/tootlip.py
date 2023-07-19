from tktooltip import ToolTip as ToolTip_base


class ToolTip(ToolTip_base):

    liveToolTips = set()
    
    def __init__(self, widget, msg = None, delay = 0, follow = True, refresh = 1, x_offset=+10, y_offset=+10, parent_kwargs = {"bg": "black", "padx": 1, "pady": 1}, **message_kwargs):
        super().__init__(widget, msg, delay, follow, refresh, x_offset, y_offset, parent_kwargs, **message_kwargs)
        self.wm_attributes('-topmost', 1)

    def _show(self) -> None:
        self.liveToolTips.add(self)
        return super()._show()

    def on_leave(self, discard=True):
        if discard:
            self.liveToolTips.discard(self)
        return super().on_leave()