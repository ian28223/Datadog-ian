
# How to use

Modify the following sections of the script with the actual command to retrieve a secret, `secret_name`.

```python
        # Command to retrieve secret_name.
        # command = [
        #     "COMMAND"
        #     , "ARGS_1"
        #     , "ARGS_2"
        #     , "ARGS_N"
        # ]
```

## Examples

### Vault

```python
        # Command to retrieve secret_name.
        command = [
            "vault"
            , "kv"
            , "get"
            , "-mount=secret"
            , "-field=passcode"
            , secret_name
        ]
```


### Azure
```python
        # Command to retrieve secret_name.
        command = [
            "az"
            , "keyvault"
            , "secret"
            , "show"
            , f'--name "{secret_name}"'
            , f'--vault-name "<your-unique-keyvault-name>"'
            , '--query "value"'
            , "-o tsv"
        ]
```


# Logging

`LOG_ENABLE = True` (Default)

The script will attempt to create a log `secret_backend_command.log` on the following directories respectively:
  - `/var/log/datadog`
  - script directory - wherever the script is located
  - `/tmp/datadog`

Logging is disabled if unable to create/write to any of above directories or if `LOG_ENABLE` is set to `False`.

# DEBUG

`DEBUG = True` (Default)

The script will log (if enabled) the full command used to retrieve the secret, the decrypted secrets, and output returned by script in plain text as seen below.

```
2024-07-15 13:28:06.725942 - Retrieving secret_name: testuser
2024-07-15 13:28:06.726066 - Command: vault kv get -mount=secret -field=passcode testuser
2024-07-15 13:28:06.747651 - error: None
2024-07-15 13:28:06.747764 - secret_value: johnny_b
2024-07-15 13:28:06.747842 - --------------------
2024-07-15 13:28:06.747964 - {"testuser": {"value": "johnny_b", "error": null}}
```

If set to `False`, the script will skip the Command and log masked secrets with the last 2 characters visible as seen below.

```
2024-07-15 13:29:12.358826 - Retrieving secret_name: testuser
2024-07-15 13:29:12.362591 - error: None
2024-07-15 13:29:12.362681 - secret_value: ******_b
2024-07-15 13:29:12.362749 - --------------------
2024-07-15 13:29:12.362851 - {"testuser": {"value": "******_b", "error": null}}
```

# TESTING

The script contains dummy key-value pairs and dummy input for testing. This allows a user to run the script by itself without needing Datadog Agent to call the script.

## `USE_TEST_INPUT = False` (Default)
The script will wait receive input that conforms to [documented example input](https://docs.datadoghq.com/agent/configuration/secrets-management/#api-example-input) from Datadog Agent or the user if run adhoc.

E.g. 
`{"version": "1.0", "secrets": ["testuser", "testpassword"]}`

If set to `True`, the script will bypass user input and retrieve the following hardcoded secrets `"testuser", "testpassword", "testempty", "testmisssing"`.

## `USE_TEST_SECRETS = True` (Default)
This allows the script to lookup a secret from hardcoded key-value pairs. Useful to test Datadog Agent secret retrieval without an actual/working `command` or keyvault to pull from.

```python
TEST_SECRETS = {
      "testuser": "johnny_b"
    , "testpassword": "secret"
    , "testempty": ""
}
```

If `command` has already been defined, the script will override the dummy TEST_SECRETS.
