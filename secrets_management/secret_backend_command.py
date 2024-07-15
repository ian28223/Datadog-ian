#!/opt/datadog-agent/embedded/bin/python
#!/usr/bin/env python3

import json
import subprocess
import sys
import os
from datetime import datetime


LOG_ENABLE = True
LOG_DIR = '/var/log/datadog/'
LOG_FILE = 'secrets_backend_command.log'

# Set DEBUG = True to mask decrypted secrets from logging.
DEBUG = True

# ====== FOR TESTING ONLY ======
TESTING = True
# Hardcoded secrets
TEST_SECRETS={
      "testuser": "john"
    , "testpassword": "secret"
    , "testempty": ""
    #, "testmissing" : # Commented out on purpose. Expecting: KeyError returned.
}

# Hardcoded input
TEST_INPUT = '{"version": "1.0", "secrets": ["testuser", "testpassword", "testempty", "testmisssing"]}'
# ====== FOR TESTING ONLY ======


def get_secret(secret_name):
    error = None
    get_secret_output = {"value": None, "error": None}
    try:
        log(f"Retrieving secret_name: {secret_name}")

        # FOR TESTING: Retrieve secret from TEST_DATA
        command = ['echo', TEST_SECRETS[secret_name]] if TESTING else None

        # Command to retrieve secret.
        # command = [
        #     "<COMMAND>"
        #     , "<ARGS_1"
        #     , "<ARGS_2"
        #     , "<ARGS_N"
        # ]

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
    if DEBUG:
        # For troubleshooting only. Comment out in production
        log(f"secret_value: {get_secret_output['value']}") 
        pass
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

def mask_string_except_last_one(input_string, mask_char='*'):
    unmasked_char_len = 2
    if len(input_string) <= unmasked_char_len:
        return input_string  # No need to mask if string length is unmasked_char_len

    masked_part = mask_char * (len(input_string) - unmasked_char_len)
    visible_part = input_string[-unmasked_char_len:]  # Last two characters of the input string

    masked_string = masked_part + visible_part
    return masked_string


def mask_output(original_output):
    masked_output = original_output.copy()
    print(f"masked_output: {masked_output}")

    for key, sval in masked_output.items():
        if isinstance(sval.get('value'), str):
            masked_output[key]['value'] = mask_string_except_last_one(sval.get('value'))
            # print(mask_string_except_last_one(sval.get('value')))
            
    # print(f"masked output: {masked_output}")
    return masked_output

def get_user_info():
    # Run the command to get detailed user information
    result = subprocess.run(['id'], stdout=subprocess.PIPE, text=True)

    # Log user context info
    user_info = result.stdout.strip()
    log(f"User information: {user_info}")

if __name__ == '__main__':    
    input_json = TEST_INPUT if TESTING else sys.stdin.read()

    if LOG_ENABLE:
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

    masked_output = mask_output(output)
    log(json.dumps(output if DEBUG else masked_output) + "\n" + "=" * 20)

    # Output to stdout for Datadog Agent
    output_json = json.dumps(output)
    print(output_json)
