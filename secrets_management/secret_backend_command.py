#!/opt/datadog-agent/embedded/bin/python
#!/usr/bin/env python3

import getpass
import json
import subprocess
import sys
import os
from datetime import datetime

# Script logging
LOG_ENABLE = True
LOG_DIR = '/var/log/datadog/'
LOG_FILE = 'secrets_backend_command.log'

# Set DEBUG = False to mask decrypted secrets from logging.
DEBUG = True

### ====== FOR TESTING ONLY ======
# Hardcoded secrets
USE_TEST_SECRETS = True
TEST_SECRETS = {
      "testuser": "johnny_b"
    , "testpassword": "secret"
    , "testempty": ""  # Empty on purpse. Expected error:"Empty string returned."
    #, "testmissing" : # Commented out on purpose. Expected error: KeyError.
}

# Hardcoded input
USE_TEST_INPUT = True
TEST_INPUT = '''{"version": "1.0", "secrets": [
      "testuser"
    , "testpassword"
    , "testempty"
    , "testmisssing"
]}'''
### ====== FOR TESTING ONLY ======

def get_secret(secret_name):
    error = None
    get_secret_output = {"value": None, "error": None}
    try:
        log(f"Retrieving secret_name: {secret_name}")

        # FOR TESTING: Retrieve secret from TEST_DATA
        command = ['echo', TEST_SECRETS[secret_name]] if USE_TEST_SECRETS else None

        # Command to retrieve secret.
        # command = [
        #     "<COMMAND>"
        #     , "<ARGS_1"
        #     , "<ARGS_2"
        #     , "<ARGS_N"
        # ]

        if DEBUG:
            # Only log command if DEBUG is True as it potentially contains sensitive arguments.
            log("Command: %s" % ' '.join(command))
              
        result = subprocess.run(command
            , text=True
            , stdout=subprocess.PIPE
        ).stdout.strip()

        # Test if resulting value is empty.
        if not result:
            error = "Empty string returned."
        else:
            get_secret_output["value"] = result
    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        error = f"Failed to retrieve secret: {message}"

    if error:
        get_secret_output["error"] = error

    # Logging
    log(f"error: {get_secret_output['error']}")
    log(f"secret_value: {get_secret_output['value'] if DEBUG else mask_string(get_secret_output['value'])}") 
    log("-" * 20)

    return get_secret_output

def list_secret_names(input_json):
    query = json.loads(input_json)
    version = query["version"].split(".")
    if version[0] != "1":
        raise ValueError(f"incompatible protocol version {query['version']}")

    names = query["secrets"]
    if not(isinstance(names, list)):
        raise ValueError(f"the secrets field should be an array: {names}")

    return names


def check_log_directory():
    global LOG_DIR, LOG_ENABLE
    # Check if the directory exists and is writable
    if os.path.exists(LOG_DIR) and os.path.isdir(LOG_DIR) and os.access(LOG_DIR, os.W_OK):
        pass
    else:
        # Create directory if not existing.
        # Fallback to script directory then /tmp directory.
        script_dir = os.path.dirname(os.path.abspath(__file__))
        log_dirs = [
            LOG_DIR
            , script_dir
            , "/tmp/datadog/"
        ]
        create_success = False
        for path in log_dirs:
            try: 
                os.makedirs(path, exist_ok=True)
                LOG_DIR = path
                create_success = True
                break
            except:
                continue

        if not create_success:
            LOG_ENABLE = False
            # For local troubleshooting only.
            # Keep commented if run by Datadog Agent.
            # print("Could not create log directory. Logging disabled.")
        else:
            # For local troubleshooting only.
            # Keep commented if run by Datadog Agent.
            # print("Logging to: %s" % LOG_DIR)
            pass


def log(message):
    if LOG_ENABLE:
        # Log the command and its output to a log file
        log_file_path = os.path.join(LOG_DIR, LOG_FILE)
        with open(log_file_path, 'a') as f:
            log_entry = f"{datetime.now()} - {message}\n"
            f.write(log_entry)

def mask_string(input_string, mask_char='*'):
    if not(isinstance(input_string, str)):
        return input_string
        
    unmasked_char_len = 2
    if len(input_string) <= unmasked_char_len:
        # No need to mask if string length is unmasked_char_len
        return input_string  

    # Last two characters of the input string
    visible_part = input_string[-unmasked_char_len:]  
    masked_part = mask_char * (len(input_string) - unmasked_char_len)

    masked_string = masked_part + visible_part
    return masked_string


def mask_output(original_output):
    masked_output = {}
    # masked_output = dict(original_output)

    for secret_name, v in original_output.items():
        secret_val = v.get('value')
        
        masked_output[secret_name] = {
            "value": mask_string(secret_val),
            "error": v.get('error'),
        }
    return masked_output
    

def get_user_info():
    user_name = getpass.getuser()
    user_id = os.getuid()
    log(f"User info: {user_name} (UID: {user_id})")
    

if __name__ == '__main__':    
    input_json = TEST_INPUT if USE_TEST_INPUT else sys.stdin.read()

    if LOG_ENABLE:
        # Check and/or create log directory
        check_log_directory()
        # Log user info
        get_user_info()


    try:
        secret_names = list_secret_names(input_json)
    except ValueError as e:
        error_msg = f"Cannot parse input: {str(e)}\nInput: {input_json}"
        log(error_msg)
        sys.exit(error_msg)

    output = {}
    log(f"Retrieving secrets: {secret_names}")
    log("-" * 20)
    for s in secret_names:
        secret_result = get_secret(s)
        output[s] = secret_result
        
    # Log output
    masked_output = mask_output(output.copy())
    output_log = output if DEBUG else masked_output
    log(json.dumps(output_log) + "\n" + "=" * 20)

    # Output to stdout for Datadog Agent
    output_json = json.dumps(output)
    print(output_json)
