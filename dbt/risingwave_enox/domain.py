class Current:
    def __init__(self, L1, L2, L3):
        self.L1 = L1
        self.L2 = L2
        self.L3 = L3

    def to_dict(self):
        return {
            "L1": self.L1.to_dict(),
            "L2": self.L2.to_dict(),
            "L3": self.L3.to_dict(),
        }


class Measurement:
    def __init__(self, centiAmpere):
        self.centiAmpere = centiAmpere

    def to_dict(self):
        return {"centiAmpere": self.centiAmpere}


class Device:
    def __init__(self, deviceId):
        self.deviceId = deviceId

    def to_dict(self):
        return {"deviceId": self.deviceId.to_dict()}


class Value:
    def __init__(self, value):
        self.value = value

    def to_dict(self):
        return {"value": self.value}


class Energy:
    def __init__(self, consumption, feedIn):
        self.consumption = consumption
        self.feedIn = feedIn

    def to_dict(self):
        return {
            "consumption": self.consumption.to_dict(),
            "feedIn": self.feedIn.to_dict(),
        }


class Reading:
    def __init__(self, wattHours):
        self.wattHours = wattHours

    def to_dict(self):
        return {"wattHours": self.wattHours}
    
class Id:
    def __init__(self, id):
        self.id = id

    def to_dict(self):
        return {"id": self.id}


class Meter:
    def __init__(self, meterId, systemTitle):
        self.meterId = meterId
        self.systemTitle = systemTitle

    def to_dict(self):
        return {
            "meterId": self.meterId.to_dict(),
            "systemTitle": self.systemTitle.to_dict(),
        }
    
class SystemTitle:
    def __init__(self, data):
        self.data = data

    def to_dict(self):
        return {"data": self.data}
    
class Owner:
    def __init__(self, id):
        self.id = id

    def to_dict(self):
        return {"id": self.id}


class Power:
    def __init__(self, draw, feed):
        self.draw = draw
        self.feed = feed

    def to_dict(self):
        return {
            "draw": self.draw.to_dict(),
            "feed": self.feed.to_dict(),
        }
    
class Watt:
    def __init__(self, watt):
        self.watt = watt

    def to_dict(self):
        return {"watt": self.watt}


class Voltage:
    def __init__(self, L1, L2, L3):
        self.L1 = L1
        self.L2 = L2
        self.L3 = L3

    def to_dict(self):
        return {
            "L1": self.L1.to_dict(),
            "L2": self.L2.to_dict(),
            "L3": self.L3.to_dict(),
        }

class DeciVolt:
    def __init__(self, deciVolt):
        self.deciVolt = deciVolt

    def to_dict(self):
        return {"deciVolt": self.deciVolt}


class SmartMeterData:
    def __init__(
        self,
        current,
        device,
        energy,
        id,
        meter,
        owner,
        power,
        readingFrom,
        receivedAt,
        voltage,
    ):
        self.current = current
        self.device = device
        self.energy = energy
        self.id = id
        self.meter = meter
        self.owner = owner
        self.power = power
        self.readingFrom = readingFrom
        self.receivedAt = receivedAt
        self.voltage = voltage


def smartMeterData_to_dict(data, ctx):
        return {
            "current": data.current.to_dict(),
            "device": data.device.to_dict(),
            "energy": data.energy.to_dict(),
            "id": data.id.to_dict(),
            "meter": data.meter.to_dict(),
            "owner": data.owner.to_dict(),
            "power": data.power.to_dict(),
            "readingFrom": data.readingFrom,
            "receivedAt": data.receivedAt,
            "voltage": data.voltage.to_dict(),
        }

def dict_to_smartMeterData(obj, ctx):
    """
    Converts object literal(dict) to a SmartMeterData instance.

    Args:
        ctx (SerializationContext): Metadata pertaining to the serialization
            operation.
        obj (dict): Object literal(dict)
    """

    if obj is None:
        return None

    return SmartMeterData(  current=obj['current'],
                            device=obj['device'],
                            energy=obj['energy'],
                            id=obj['id'],
                            meter=obj['meter'],
                            owner=obj['owner'],
                            power=obj['power'],
                            readingFrom=obj['readingFrom'],
                            receivedAt=obj['receivedAt'],
                            voltage=obj['voltage'],
                        )
