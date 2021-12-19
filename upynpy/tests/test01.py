from upynpy import scan

def scan_test():
    devices = scan()
    methods = (
        {
            "name": "GetExternalIPAddress", 
            "args": {},
        }, 
        {
            "name": "AddPortMapping",
            "args":{
                "NewRemoteHost":"", 
                "NewExternalPort":9082, 
                "NewProtocol":"TCP", 
                "NewInternalPort":9082,
                "NewInternalClient":"191.168.1.4",
                "NewEnabled": True,
                "NewPortMappingDescription":"nothing-he",
            }
        },{
            "name": "GetSpecificPortMappingEntry",
            "args":{
                "NewRemoteHost":"", 
                "NewProtocol":"TCP", 
                "NewExternalPort": 9082, 
            }
        }
    )
 
    for dev in devices:
        result = {}
        for m in methods:
            if dev.has_action(m["name"]):
                f = dev.action.get(m["name"])
                print(f"method: {f}")
                # ^ equals to dev.action.GetExternalIPAddress

                result[m["name"]] = f(**m["args"])
        if result:
            print(result)
            print("<{}>".format("-" * 100))


if __name__ == "__main__":
    scan_test()