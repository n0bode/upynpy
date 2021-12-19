from xml.etree import ElementTree as ET
from xml.etree.ElementTree import tostring
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from upynpy.errors import UpnpError

soap_envelope = "http://schemas.xmlsoap.org/soap/envelope/"
soap_encoding = "http://schemas.xmlsoap.org/soap/encoding/"
soap_schema = "urn:schemas-upnp-org:control-1-0"

def mount_header(service : str, action_name : str):
    return {
        "Content-Type": "text/xml",
        "SOAPAction": f'"{service}#{action_name}"'
    }

def mount_soap(action_name : str, service : str, args : list):
    root = ET.Element("s:Envelope")
    root.set("xmlns:s", soap_envelope)
    root.set("s:encodingStyle", soap_encoding)
    body = ET.SubElement(root,"s:Body")
    act = ET.SubElement(body, "u:"+action_name)
    act.set("xmlns:u", service)
    for key, value in args.items():
        et = ET.SubElement(act, key)
        et.text = str(value)
    return root

def decode(action_name: str, service: str, body: str) -> dict:
    """
        decode response upnp to dict
    """
    xresp = ET.fromstring(body)
    xpath = f"{{{service}}}{action_name}Response"
    # ^ i'd like remove that, but we need namespace to access response
    for x in xresp.iter(xpath):
        for xy in x:
            yield (xy.tag, xy.text) 


def handle_error(err : HTTPError) -> Exception:
    try:
        root = ET.fromstring(err.read())
        for x in root.iter(f"{{{soap_schema}}}UPnPError"):
            code = x.find(f"{{{soap_schema}}}errorCode").text
            description = x.find(f"{{{soap_schema}}}errorDescription").text
            return UpnpError(description, code)
    except:
        return err

def request (action : dict, **kargs : dict) -> dict:
    url : str = action["control"]
    name : str = action["name"]
    service : str = action["service"]

    payload = mount_soap(name, service, kargs)
    dumps = tostring(payload)
    try:
        req = Request(url, data=dumps, headers=mount_header(service, name), method="POST")
        resp = urlopen(req)
        return decode(name, service, resp.read())
    except HTTPError as err:
        raise handle_error(err)
    except Exception as err:
        raise err
