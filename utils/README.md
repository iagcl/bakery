# Assume Role Script

## Run Bootstrap

This will create the bash script for assuming roles in burger accounts. Based on your credentials, it will dynamically query what roles you can assume and creates the `assume.sh` bash script for day to day use.

Ensure your Bakery AWS account's credentials are in the default section of `~/.aws/credentials`.

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
