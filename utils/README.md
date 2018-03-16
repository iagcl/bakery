Assume Role Script

***

## Run bootstrap

This will create the bash script for assuming roles in burger accounts. Based on your credentials, it will dynamically query what roles you can assume and creates the `assume.sh` bash script for day to day use. A soft link will be created in your `/usr/local/bin/assume` path so that you can just run the script as the command `assume` anywhere

```bash
$ make bootstrap-assume-script
```

> **Rerun bootstrap if your permissions have been changed in Bakery**

## Use assume.sh

```bash
$ source assume [-h] {number}
```

## Example

* `source assume`
* `source assume 0`
* `source assume -h`
