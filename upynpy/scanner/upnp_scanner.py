from socket import socket, SOCK_DGRAM, IPPROTO_UDP, AF_INET, timeout
from typing import List
from xml.etree import ElementTree as xml
from urllib.request import urlopen
from urllib.parse import urlparse
from urllib.error import HTTPError
from http.client import BadStatusLine
from upynpy.device import UpnpDevice

__search_role = (\
    'M-SEARCH * HTTP/1.1\r\n' \
    'HOST:239.255.255.250:1900\r\n' \
    'ST:upnp:rootdevice\r\n' \
    'MX:2\r\n' \
    'MAN:"ssdp:discover"\r\n' \
    '\r\n').encode("utf-8")
 

def __decode_raw(text : str) -> dict:
    headers : dict = {}
    lines = text.split("\n")
    if not lines:
        raise Exception("status not found")

    code = lines.pop(0)
    for line in lines:
        line = line.strip()
        if not line:
            continue
        key, value = line.split(":", 1)
        headers[key.upper()] = value.strip()
    return headers

def namespace(root):
    return root.tag.split("}", 1)[0] + "}"

def __fetch_scpd(location : str):    
    """
        Call location for gets scpd xml
    """
    try:
        resp = urlopen(location)
        text = resp.read()
        data = xml.fromstring(text)
        return data
    except Exception as err:
        raise err

def __list_devices_from_scpd(root: xml.Element) -> List[dict]:
    base = namespace(root)
    for item in root.iter():
        if not item.tag.endswith("device"):
            continue
        yield item

def __device_description_from_node(device : xml.Element) -> dict: 
    base = namespace(device)
    name = device.find(f"{base}friendlyName").text
    description = device.find(f"{base}modelDescription").text

    return {
        "name": name,
        "description": description,
    }

def __services_from_devices(location: str, device : xml.Element):
    """
        decode scpd xml to dict 
    """
    url = urlparse(location)    
    base = namespace(device)

    # honestely, xml in python is not good, 
    # cos we need especify all time namespace 
    for n in device.iter(f"{base}service"):
        serv : dict = {}
        for a in n:
            name = a.tag[len(base):]
            value = a.text
            if name.endswith("URL"):
                value = f"{url.scheme}://{url.netloc}/{value.lstrip('/')}"
            serv[name] = value
        yield serv

def __map_args_from_scpd(root : xml.Element) -> dict:
    base = namespace(root)
    args : dict = {}
    add_if = lambda d, v, n: d.update({n : v}) if v else d

    for var in root.iter(f"{base}stateVariable"):
        name = getattr(var.find(f"{base}name"), "text")
        if not name:
            continue
        arg : dict = {
            "related_name": name
        }

        dfault = getattr(var.find(f"{base}defaultValue"), "text", None)
        if dfault:
            arg["default"] = dfault

        dtype = getattr(var.find(f"{base}dataType"), "text", "all")
        if dtype:
            arg["type"] = dtype

        allows = var.find(f"{base}allowedValueList")

        allows = [] if allows == None else allows
        for a in allows:
            if not "allowed" in arg:
                arg["allowed"] = []
            arg["allowed"].append(a.text)
        args[name] = arg
    return args


def __get_actions(services : list):
    actions : dict = {}
    for serv in services:
        scpdurl : str = serv.get("SCPDURL")         
        # theres is not scpdurl
        if not scpdurl:
            continue

        try:
            resp = urlopen(scpdurl)
            scpd = xml.fromstring(resp.read())

            maps_args = __map_args_from_scpd(scpd)

            base : str = namespace(scpd)
            empty = xml.Element("a")
            empty.text = "undefined"

            for a in scpd.iter(f"{base}action"):
                args : dict = {}
                ac_name : str = a.find(base+"name").text
                for aa in a.iter(base+"argument"):
                    arg_name : str = getattr(aa.find(base+"name"), "text", "undefined")
                    arg_type : str = getattr(aa.find(base+"direction"), "text", "undefined")
                    related : str = getattr(aa.find(base+"relatedStateVariable"), "text", None)
                    if not arg_type in args:
                        args[arg_type] = {}
                        
                    args[arg_type][arg_name] = {**maps_args.get(related, {}), "name": arg_name}                
                actions[ac_name] = {
                    "arguments": args,
                    "name": ac_name,
                    "control": serv["controlURL"],
                    "service": serv["serviceType"],
                    "scpd": serv["SCPDURL"]
                }
        except (HTTPError, BadStatusLine) as err:
            pass
        except Exception as err:
            print(err)
            raise err
    return actions

def scan(duration : int = 2) -> List[UpnpDevice]:
    """
        search for upnp devices
    """

    s = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
    s.settimeout(duration)
    s.sendto(__search_role, ('239.255.255.250', 1900) )

    routers = []
    try:
        # searching devices actived upnp in our network
        while True:
            data, addr = s.recvfrom(65507)
            routers.append({
                "addr": dict(zip(("ip", "port"), addr)), 
                "headers": __decode_raw(data.decode())
            })
    except timeout:
        # ^ timeout because we send a broadcast in our network
        # so, we dont know how many devices exists in it
        # we need wait for them answer us
        pass
    except Exception as err:
        raise err
    
    ndevices = []
    try:
        for router in routers:
            location : str = router["headers"]["LOCATION"]
            scpd = __fetch_scpd(location)
            # ^ capture scpd xml file
            for device in __list_devices_from_scpd(scpd):
                desc = __device_description_from_node(device)
                # ^ reads info about device
                services = __services_from_devices(location, device)
                # ^ reads services from scpd xml
                actions = __get_actions(services)
                # ^ captures actions of services 
                ndevices.append(UpnpDevice({**router, **desc, "actions": actions}))
    except Exception as err:
        raise err

    return ndevices