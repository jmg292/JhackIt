import os
from pyrcrack.scanning import Airodump


class EasyDump(Airodump):

    """
        Out of the box, pyrcrack.scanning.Airodump continually spawns a million separate instances.
        This is not okay under most circumstances, but it's especially not okay on my tiny Raspberry Pi Zero.
        Override the start method to fix this behavior.

        In addition, add support for multiple output formats and the "channel" argument.
        This'll allow us to capture a handshake in addition to reading process output when it's time to run
        a deauth attack
    """

    def __init__(self, interface=False, **kwargs):
        # Add support for the airodump-ng "channel" argument
        allowed_argument_list = list(self._allowed_arguments)
        allowed_argument_list.append(("channel", False))
        self._allowed_arguments = tuple(allowed_argument_list)
        super(Airodump, self).__init__(**kwargs)
        self.interface = interface
        self._capturing_packets = False
        self.started = False

    def get_clients(self):
        """
            Out of the box, pyrcrack.scanning.Airodump.clients returns a list of lists of uncategorized information.
            The output from airodump gives us headers that can be used to categorize that information.
            Apply those headers, and return a list of dictionaries.
        :return:
            A list of dictionaries containing categorized client information.
        """
        return_value = []
        client_information_keys = [
            "Station MAC",
            "First time seen",
            "Last time seen",
            "Power",
            "# packets",
            "BSSID",
            "Probed ESSIDs"
        ]
        client_list = super().clients
        for uncategorized_client_info in client_list:
            categorized_client_info = {}
            for i in range(0, len(client_information_keys)):
                categorized_client_info[client_information_keys[i]] = uncategorized_client_info[i]
            return_value.append(categorized_client_info)
        return return_value

    def stop(self):
        super().stop()

    def start(self, _=False, output_pcap=False):
        if not self.started:
            if output_pcap:
                # Output to multiple formats, which will allow a handshake to be captured and analyzed later
                self._exec_args = list(self._exec_args)
                self._exec_args.append(("output-format", "csv"))
                self._exec_args.append(("output-format", "pcap"))
                self._capturing_packets = True
            super().start(_)
            self.started = True
