import socket
import struct
from datetime import datetime
from plyer import notification
import tkinter as tk
import threading
import os
import re

# Initialising the list of servers as an empty list, which populates automatically by the score grabber
serverlist = []

# Get current PC's IPv4 address to initialise it as default IP
current_pc_name = socket.gethostname()
current_ipv4 = socket.gethostbyname(current_pc_name)

# Initialize default values for IP address and port
UDP_IP = current_ipv4
UDP_PORT = 5005

# Create the main window
root = tk.Tk()
root.title("Admin Scanner")

# Create labels and entry boxes for IP address and port
ip_label = tk.Label(root, text="UDP IP address:")
ip_entry = tk.Entry(root, width=30)
ip_entry.insert(0, UDP_IP)

port_label = tk.Label(root, text="UDP port:")
port_entry = tk.Entry(root, width=30)
port_entry.insert(0, UDP_PORT)

# Create a console log text widget
console_log = tk.Text(root, width=100, height=10)
console_log.config(state="disabled")

# Create a label to contain server ports and scores
info_label = tk.Label(root, text=f"No Servers")

# Define a function to update the IP and port variables
def update_variables():
    global UDP_IP, UDP_PORT
    UDP_IP = ip_entry.get()
    UDP_PORT = int(port_entry.get())

# Define a function to display notifications and log them in the console
def display_notification(data, addr):
    if "admin" in str(data).lower():
        clientname = addr[0] + ":" + str(addr[1])
        timestamp = datetime.now().strftime("%H:%M:%S")
        message = f"{clientname} called for an admin."
        print(timestamp, "---", str(clientname), "-", "Called for an admin")
        console_log.config(state="normal")
        console_log.insert(tk.END, f"{timestamp} --- {clientname} - Called for an admin\n")
        console_log.config(state="disabled")
        notification.notify(title="Admin Notification",
                            message=message,
                            app_name="CSGO Admin Scanner",
                            timeout=5)

# Define a function to display scores and log them in the console
def display_scores(data, addr): 
    if "matchstatus: score:" in str(data).lower():
        clientname = addr[0] + ":" + str(addr[1])
        timestamp = datetime.now().strftime("%H:%M:%S")
        message = f"{clientname} ended a round."
        match_score = data.split(b"Score: ")[1].split(b" on")[0].decode()
        print(match_score)
        if any(addr[1] in i for i in serverlist):
            print("Server already in serverlist")
            serverscore = [addr[1], match_score]
            for o in serverlist:
                counter = 0
                if serverlist[counter][0] == addr[1]:
                    print("Index Confirmed")
                else:
                    print("Incrementing Counter")
                    counter += 1
            serverlist[counter] = serverscore
            print(serverlist)
            info_label.config(text=f"{serverlist}")
        else:
            serverscore = [addr[1], match_score]
            serverlist.append(serverscore)
            print("Server added to list")
            info_label.config(text=f"{serverlist}")

# Define a function to run the scanner
def run_scanner():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    print("Scanner active!")
    print(f"Your UDP IP is set to {UDP_IP}:{UDP_PORT} - make sure the CSGO servers are set to log to that IP!")
    console_log.config(state="normal")
    console_log.insert(tk.END, "Scanner active!\n")
    console_log.config(state="disabled")
    while True:
        data, addr = sock.recvfrom(1024)
        display_notification(data, addr)
        display_scores(data, addr)
        
# Define a function to start the scanner in a separate thread
def start_scanner():
    update_variables()
    scanner_thread = threading.Thread(target=run_scanner)
    scanner_thread.start()

# Define a function to clear the console log except for the latest line
def clear_log():
    console_log.config(state="normal")
    last_line_index = console_log.index(tk.END+"-2c").split(".")[0] + ".0"
    console_log.delete("1.0", last_line_index)
    console_log.config(state="disabled")

# Create a label widget for instructions
instructions_label = tk.Label(root, text="Click Start Scanner, echo admin in a server, then click Start Scanner again to initialise.")

# Create a button to start the scanner
start_button = tk.Button(root, text="Start Scanner", command=start_scanner)

# Create a button to clear the console log
clear_button = tk.Button(root, text="Clear Log", command=clear_log)

# Pack all the widgets into the main window
ip_label.pack()
ip_entry.pack()
port_label.pack()
port_entry.pack()
instructions_label.pack()
start_button.pack()
clear_button.pack()
console_log.pack()
info_label.pack()

# Start the main event loop
root.mainloop()
