## Keyring

### Overview

* The Python keyring library provides an easy way to access the system keyring service from python. It can be used in any application that needs safe password storage.

### Initialize the KeyringManager

```python
from credential_bridge import KeyringManager


my_keyring = KeyringManager(
    service_name="your_service_name"
)
```
### Add a secret
```
my_keyring.add_secret(name, secret)
```

### Get a secret
```
my_keyring.get_secret(name)
```

### Update a secret
```
my_keyring.update_secret(name, secret)
```

### Delete a secret
```
my_keyring.delete_secret(name)
```