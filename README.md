# Jhack-It

   Webapp that lives in my jacket

## What?

   This project provides a convenient-to-use interface for a back-end that wraps a few tools from the Aircrack-NG suite.  It is deployed on a Raspberry Pi Zero W that lives in my jacket.

## Why?

   There have been a number of locations from which I needed to capture a WPA2 handshake, but into which I couldn't bring a laptop.  And it wasn't really an option to sit outside with a laptop, or use a cantenna.  
   
   In all of these locations, however, I could bring a jacket.  Enter: Jhack-It.  Now I can sit around and "play on my phone" while, in reality, using this webapp and the hardware embedded in my jacket to capture that handshake without raising any eyebrows.
   
### But really.... why? There are so many better ways.

   Yep, there are.  My way's more fun though.  Plus, the Airodump UI always kinda bugged me, so now I have something that could be more pleasant to use with a bit of polish.
   
## How?

   There's an existing Python module called pyrcrack that wraps the Aircrack-NG suite of tools that's the foundation of this application.  Although, saying it "wraps" the suite is a bit generous.  It *tries* to wrap that suite, but version 0.1.1 (the version in PyPI at the time of this writing), is really, really broken
   
   First thing this application does is provide a wrapper around the pyrcrack module to make it actually work.  Then provides a few POST and GET HTTP methods to interact with that module.
   
   The last piece to the puzzle is a web UI that attempts to use AngularJS to provide a closer coupling between the scan state and the user, and uses MaterializeCSS to make it nice to look at.  
   
   The result is a webapp that allows a user to scan nearby access points, pick one, and then launch a deauth attack and store the results of that attack in a pcap file for later access.
