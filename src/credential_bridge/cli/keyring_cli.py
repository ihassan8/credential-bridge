import argparse

from ..keyring_manager import KeyringManager

# import logging


def handle_commands(manager, action, service_name, name, secret):
    if action in ["add", "update"]:
        if not secret:
            print("ℹ️ Password is required for adding or updating credentials❗")
            return
        if action == "add":
            try:
                manager.add_secret(name, secret)
                print(f"👍 Credentials successfully added: \nSystem: {service_name}\nName: {name}\nSecret: {secret}")
            except Exception as e:
                print(f"ℹ️ Failed to add {name} for {service_name}: {e}❗")
        else:
            try:
                manager.update_secret(name, secret)
                print(f"👍 Credentials successfully updated: \nSystem: {service_name}\nName: {name}\nSecret: {secret}")
            except Exception as e:
                print(f"ℹ️ Failed to update {name} for {service_name}: {e}❗")
    elif action == "get":
        try:
            secret_value = manager.get_secret(name)
            if secret_value:
                print(
                    f"👍 Credentials successfully retrieved: \nSystem: {service_name}\nName: {name}\nSecret: {secret_value}"
                )
            else:
                print(f"ℹ️ No secret found for {name}❗")
        except Exception as e:
            print(f"ℹ️ Failed to retrieve {name} for {service_name}: {e}❗")
    elif action == "delete":
        try:
            manager.delete_secret(name)
            print(f"👍 Credentials successfully deleted: \nSystem: {service_name}\nName: {name}")
        except Exception as e:
            print(f"ℹ️ Failed to delete {name} for {service_name}: {e}❗")


def main():
    parser = argparse.ArgumentParser(description="Keyring CLI")
    parser.add_argument("action", choices=["add", "get", "delete", "update"], help="Action to perform")
    parser.add_argument("--service-name", required=True, help="Service name for the credential")
    parser.add_argument("--name", help="Name of the secret")
    parser.add_argument("--secret", help="Value of the secret")

    args = parser.parse_args()

    # logging.basicConfig(level=logging.DEBUG)
    # logger = logging.getLogger(__name__)

    manager = KeyringManager(service_name=args.service_name)

    handle_commands(manager, args.action, args.service_name, args.name, args.secret)


if __name__ == "__main__":
    main()
