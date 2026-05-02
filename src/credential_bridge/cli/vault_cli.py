import argparse
import json

from prompt_toolkit import print_formatted_text
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.styles import Style

# from ..utils import get_vault_credentials
from ..vault_manager import VaultManager

# import logging


json_style = Style.from_dict(
    {
        "output": "fg:ansiyellow italic",
    }
)


def handle_commands(manager, action, service_name, secret, versions=None):
    if action == "add":
        try:
            manager.add_secret(service_name, secret)
            print(f"👍 Credentials successfully added: \nName: {service_name}\nSecret: {secret}")
        except Exception as e:
            print(f"ℹ️ Failed to add {secret} for {service_name}: {e}❗")
    elif action == "get":
        try:
            secret_value = manager.get_secret(service_name)
            if secret_value:
                print(f"👍 Credentials successfully retrieved for {service_name}:")
                formated_json = json.dumps(secret_value, indent=4)
                print_formatted_text(HTML(f"<output>{formated_json}</output>"), style=json_style)
            else:
                print(f"ℹ️ No credentials found for {service_name}❗")
        except Exception as e:
            print(f"ℹ️ Failed to retrieve credentials for {service_name}: {e}❗")
    elif action == "get-config":
        try:
            secret_value = manager.get_config(service_name)
            if secret_value:
                print(f"👍 Configuration successfully retrieved: \nName: {service_name}\nSecret: {secret_value}")
            else:
                print(f"ℹ️ No Configuration found for {service_name}❗")
        except Exception as e:
            print(f"ℹ️ Failed to retrieve configuration for {service_name}: {e}❗")
    elif action == "delete":
        try:
            manager.delete_secret(service_name)
            print(f"👍 Credentials successfully deleted: \nName: {service_name}")
        except Exception as e:
            print(f"ℹ️ Failed to delete credentials for {service_name}: {e}❗")
    elif action == "update":
        try:
            manager.update_secret(service_name, secret)
            print(f"👍 Credentials successfully updated: \nName: {service_name}\nCredentials: {secret}")
        except Exception as e:
            print(f"ℹ️ Failed to update {secret} for {service_name}: {e}❗")
    elif action == "list":
        try:
            secrets = manager.list_secrets(service_name)
            print(f"👍 Secrets listed: \nName: {service_name}\nCredentials: {secrets}")
        except Exception as e:
            print(f"ℹ️ Failed to list secrets in path '{service_name}': {e}❗")
    elif action == "read-metadata":
        try:
            metadata = manager.read_secret_metadata(service_name)
            if metadata:
                print(f"👍 Metadata successfully retrieved for {service_name}:")
                formated_json = json.dumps(metadata, indent=4)
                print_formatted_text(HTML(f"<output>{formated_json}</output>"), style=json_style)
            else:
                print(f"ℹ️ No metadata found for {service_name}❗")
        except Exception as e:
            print(f"ℹ️ Failed to read metadata for secret '{service_name}': {e}❗")
    elif action == "delete-versions":
        try:
            manager.delete_secret_versions(service_name, versions)
            print(f"👍 Deleted versions {versions} of secret '{service_name}'")
        except Exception as e:
            print(f"ℹ️ Failed to delete versions {versions} of secret '{service_name}': {e}❗")
    elif action == "undelete-versions":
        try:
            manager.undelete_secret_versions(service_name, versions)
            print(f"👍 Undeleted versions {versions} of secret '{service_name}'")
        except Exception as e:
            print(f"ℹ️ Failed to undelete versions {versions} of secret '{service_name}': {e}❗")
    elif action == "destroy-versions":
        try:
            manager.destroy_secret_versions(service_name, versions)
            print(f"👍 Destroyed versions {versions} of secret '{service_name}'")
        except Exception as e:
            print(f"ℹ️ Failed to destroy versions {versions} of secret '{service_name}': {e}❗")


def main():
    parser = argparse.ArgumentParser(description="Vault CLI")
    parser.add_argument(
        "action",
        choices=[
            "add",
            "get",
            "get-config",
            "delete",
            "update",
            "list",
            "read-metadata",
            "delete-versions",
            "undelete-versions",
            "destroy-versions",
        ],
        help="Action to perform",
    )
    parser.add_argument("--vault-token", help="Vault token for authentication")
    parser.add_argument("--vault-role-id", help="Vault AppRole role ID for authentication")
    parser.add_argument("--vault-secret-id", help="Vault AppRole secret ID for authentication")
    parser.add_argument(
        "--service-name", default="default_service", help="Service name for the secret (default: default_service)"
    )
    parser.add_argument("--secrets", action="append", help="Secrets to add.update in the form key=value")
    parser.add_argument("--versions", action="append", type=int, help="Versions of the secret to operate on")
    parser.add_argument("--mount-point", help="Mount point for Vault secrets")

    args = parser.parse_args()

    # logging.basicConfig(level=logging.INFO)
    # logger = logging.getLogger(__name__)

    # vault_token, vault_role_id, vault_secret_id = get_vault_credentials()

    # Use provided credentials or fall back to config file
    # vault_token = args.vault_token or vault_token
    # vault_role_id = args.vault_role_id or vault_role_id
    # vault_secret_id = args.vault_secret_id or vault_secret_id

    manager = VaultManager(
        vault_token=args.vault_token,
        vault_role_id=args.vault_role_id,
        vault_secret_id=args.vault_secret_id,
        service_name=args.service_name,
        mount_point=args.mount_point,
    )

    secret_data = {}
    if args.secrets:
        for secret in args.secrets:
            key, value = secret.split("=", 1)
            secret_data[key] = value

    handle_commands(manager, args.action, args.service_name, secret_data, args.versions)


if __name__ == "__main__":
    main()
