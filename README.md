# Upynpy is a simple library to use Upnp devices

## Example

```python
from upynpy import scan
from upynpy.errors import UpnpError

devices = scan()

for dev in devices:
  print("Found :", dev)
  print("actions avaliables:")
  for ac in dev.actions:
    print(ac)
  print("### END")
  
  if dev.has_action("GetExternalIPAddress"):
    action = dev.action.GetInternalIPAddress
    resp = action()
    for name, key in resp.items():
      print(f"{name}: {key}")
  
  # checks if action exists
  if dev.has_action("AddPortMapping"):
    try:
      res = dev.action.AddPortMapping(
        NewInternalPort=8081,
        NewExternalPort=8081,
        NewEnabled=True,
        NewRemoteHost="", # you can omit it
        NewInternalClient="{youriplocal}",
        NewPortMappingDescription="Name"
      )
      print("configured new port mapping")
    except UpnpError as err:
      print("Something is wrong!!!")
      print(err)
```
