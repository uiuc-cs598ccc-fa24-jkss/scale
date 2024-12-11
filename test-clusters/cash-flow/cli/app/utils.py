import os
import sys
import subprocess

def run(command, stream=print, capture_output=False, live_output=False, directory=None):
    """Run a shell command and stream output."""
    # stream(f"Running command: {command}")

    if directory:
        os.chdir(directory)

    # Use subprocess.Popen to stream output in real-time
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    output = ""
    # Stream stdout and stderr
    while True:
        pout = process.stdout.readline()
        if pout == "" and process.poll() is not None:
            break
        if pout:
            output += pout
            if live_output:
                stream(pout.strip())
    
    # Handle any remaining stderr output
    stderr = process.stderr.read().strip()
    if stderr:
        stream(f"Error: {stderr}")
    
    if capture_output:
        return output
    # Return the exit code
    return process.poll()


def update_env_file(file_path, variable, value):
    """Update or append an environment variable in a .env file."""
    updated = False
    lines = []

    # Read the existing lines in the .env file
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            lines = f.readlines()

    # Check if the variable already exists and update its value
    with open(file_path, 'w') as f:
        for line in lines:
            if line.startswith(f"{variable}="):
                f.write(f"{variable}={value}\n")  # Update existing variable
                updated = True
            else:
                f.write(line)

        # If the variable wasn't found, append it
        if not updated:
            f.write(f"{variable}={value}\n")

def sys_path_append(path):
    if path not in sys.path:
        sys.path.append(path)

def sys_path_insert(path):
    if path not in sys.path:
        sys.path.insert(0, path)
    
    