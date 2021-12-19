from . import UpnpAction

class ActionGenerator:
    def __init__(self, device, actions):
        self._device = device
        self._actions = actions

    def __getattribute__(self, name : str) -> UpnpAction:
        try:
            return object.__getattribute__(self, name)
        except:
            pass

        actions : dict = object.__getattribute__(self, "_actions")
        device = object.__getattribute__(self, "_device")

        func = actions.get(name)
        if not func:
            raise Exception(f"'{name}' action not found in {device.__str__()}")
        return UpnpAction(device, func)

    def __getattr__(self, name):
        ActionGenerator.__getattribute__(self, name)
    
    def get(self, name):
        return ActionGenerator.__getattribute__(self, name)
    