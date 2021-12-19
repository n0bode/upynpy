from typing import List
from upynpy.request import request

types = {
    "string": str,
    "ui4": int,
    "ui2": int,
    "ui8": int,
    "boolean": bool,
    "float": float,
    "all": "any"
}

def assert_type (field, kind, value, allow):
    tp = types.get(kind, "all")
    if tp == types["all"]:
        tp = (int, bool, str, float)

    if not isinstance(value, tp):
        raise TypeError(f"'{field}' must be type {tp.__name__} not {type(value).__name__}")

    if allow and not value in allow:
        raise ValueError(f"{field}' value must be {allow}")
    
class UpnpAction:
    def __init__(self, device, action):
        self._action = action
        self._device = device
    
    @property
    def parameters(self) -> List[str]:
        return self._action["arguments"].get("in", {}).values()
    
    @property
    def returns(self) -> List[str]:
        return self._action["arguments"].get("out", {}).values()
    
    @property
    def name(self) -> str:
        return self._action["name"]

    def __call__(self, *args, **kargs):
        nargs = {}
        for arg in self.parameters:
            var = arg["name"]
            val = kargs.get(var)
            kind = arg["type"]

            if not var in kargs:
                if not "default":
                    raise Exception(f"missing '{var}' as parameter {self.name} action") 
                val = types.get(kind, str)(arg.get("default", ""))

            assert_type(var, arg["type"], val, arg.get("allowed", []))
            nargs[var] = {"boolean": int}.get(kind, lambda x: x)(val)
        
        # responses from xml
        response : dict = {}
        for name, text in request(self._action , **nargs):
            response[name] = types.get(self._action["arguments"]["out"][name]["type"], str)(text)
        return response
            

    def __str__(self): 
        arg_to_str = lambda x: "{name}: {type}".format(**{**x, "type": types[x["type"]].__name__})

        args = ", ".join(map(arg_to_str, self.parameters))
        rets = ", ".join(map(arg_to_str, self.returns))
        return f"{str(self._device)}::{self.name} ({args}) -> ({rets})"  

        
