import json


class JhackItConfig(object):

    def __init__(self, bind_port=80, bind_address="0.0.0.0", scan_interface="wlan1", **kwargs):
        self.bind_port = bind_port
        self.bind_address = bind_address
        self.scan_interface = scan_interface

    def to_json(self):
        return json.dumps(self.__dict__, sort_keys=True, indent=4)

    @staticmethod
    def from_json(input_json):
        config_data = json.loads(input_json)
        return JhackItConfig(**config_data)


if __name__ == "__main__":
    """
        Regenerate configuration file
    """
    new_config = JhackItConfig()
    with open("config.json", "w") as outfile:
        outfile.write(new_config.to_json())
    # Validate new configuration
    with open("config.json", "r") as infile:
        validation = JhackItConfig.from_json(infile.read())
    print(validation.__dict__)
