from upynpy.action import UpnpAction
from upynpy.action.action_generator import ActionGenerator

class UpnpDevice:
    def __init__(self, device):
        self._device = device
    
    @property
    def name(self) -> str:
        return self._device["name"]

    @property
    def description(self) -> str:
        return self._device["description"]
    
    @property
    def desc_location(self) -> str:
        return self._device["headers"]["LOCATION"]
    
    @property
    def scpd_location(self) -> str:
        return ""

    @property
    def action(self) -> ActionGenerator:
        return ActionGenerator(self, self._device["actions"])

    @property
    def actions(self) -> list:
        return self._device["actions"].keys()

    def has_action(self, name):
        return name in self._device["actions"]
            
    @property
    def addr(self) -> (str, int):
        return self._device["addr"]

    def refresh(self):
        """
            Refresh actions from scpd upnp device
        """
        pass

    def __str__(self):
        return f"Device::{self.addr['ip']}:{self.addr['port']}@{self.name}"

if __name__ == "__main__":
    d = UpnpDevice({"name": "ok", "addr":("0.0.0.0", "9090")})
    print(d.name)
    print(d)