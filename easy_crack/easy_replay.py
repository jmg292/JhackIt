from pyrcrack.replaying import Aireplay


class EasyDeauth(Aireplay):

    def __init__(self, interface=False, **kwargs):
        """
            Out of the box, Aireplay.__init__ will raise a WrongArgument exception,
             even though every argument provided is correct.
            This is because it adds "attack" to the kwargs, but that's not on the list of approved keyword arguments.
            Fix that by not calling Aireplay.__init__, then manually setting up _exec_args and the interface.
        """
        super(Aireplay, self).__init__()
        self.interface = interface
        self._exec_args = [(x, y) for x, y in kwargs.items()]

    def watch_process(self):
        """
            Out of the box, Aireplay is set up to run until self.stop() is called.  This is a bad policy.
            Fix it by overriding the watchdog method.
        """
        return False

    def start(self, deauth_count=10):
        self._exec_args.append(("0", str(deauth_count)))
        print(["aireplay-ng"] + self.flags + self.arguments + [self.interface])
        super().start()
