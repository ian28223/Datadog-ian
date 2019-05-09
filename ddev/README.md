# Overview

This script will perform the following:

- Installs [Pyenv][1]
- Installs the latest Python 3.x.x (which will be set as the current/global Python)
- Installs the latest Python 2.x.x (for you to switch over too if you need)
- Clones [Datadog/integrations-core repo][2]
- Clones [Datadog/integrations-extras repo][3]
- Finally, installs [`ddev`][4]

## Installation

### One-line install command

```
eval "$(curl https://raw.githubusercontent.com/ian28223/Datadog-ian/master/ddev/pyenv_ddev_setup.sh)"
```


### Ideally, you sould inspect scripts from strangers before running them.

- Download the script

    ```
    curl -O https://raw.githubusercontent.com/ian28223/Datadog-ian/master/ddev/pyenv_ddev_setup.sh
    ```

- Inspect the contents

    ```
    vim pyenv_ddev_setup.sh
    ```

  OR

    ```
    nano pyenv_ddev_setup.sh
    ```

- Run the script

    ```
    source pyenv_ddev_setup.sh
    ```


## Notes

- The script has been tested and found working on Ubuntu 16 (Xenial) and Ubuntu 18 (Bionic)
- Ubuntu 14 (Trusty) might work by using just Python2.
  - Python3 requires Openssl 1.0.2 which is not readily available in Trusty.
  - Comment [this line][5] so as not to attempt installation of Python3.
  - Change `pyglobal` to `py2latest` (here)[6]
- Might also work in Mac OSX.
  - Need to install XCode from Apple App Store manually.
  - The scrip will attempt to installs Homebrew as well.

[1]: https://github.com/pyenv/pyenv
[2]: https://github.com/DataDog/integrations-core
[3]: https://github.com/DataDog/integrations-extras
[4]: https://github.com/DataDog/integrations-core/tree/master/datadog_checks_dev
[5]: https://github.com/ian28223/Datadog-ian/blob/master/ddev/pyenv_ddev_setup.sh#L68
[6]: https://github.com/ian28223/Datadog-ian/blob/master/ddev/pyenv_ddev_setup.sh#L70L74
