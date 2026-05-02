import json
import logging
import os
import socket
from enum import Enum
from pathlib import Path

import requests

CONFIG_FILE = os.path.join(os.getenv("USERPROFILE") or os.getenv("HOME"), ".vault_config.json")

logger = logging.getLogger(__name__)


# Utility Functions
class VaultAddr(Enum):
    Host_1 = "https://vault-ent.acme.com"
    Host_2 = "https://vault-ent.acme.org"

    def __str__(self):
        return self.value


def get_user_profile_path() -> Path:
    """
    Get the user profile path for the current operating system.

    Returns:
        Path: User's profile directory.
    """
    profile_path = os.environ.get("USERPROFILE") if os.name == "nt" else os.environ.get("HOME")
    if not profile_path:
        raise EnvironmentError("User profile path could not be determined.")
    return Path(profile_path)


def local_path(relative_path):
    """Get local path of resource file"""
    base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


def load_welcome_banner(file_path):
    with open(local_path(file_path), "r", encoding="utf-8") as file:
        return file.read()


def get_domain():
    try:
        domain = socket.getfqdn()
        if "." in domain:
            domain = domain.lower().split(".")[1]
        return domain
    except Exception as err:
        logger.error(f"Unable to get domain: {err}")
        return None


def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)


def load_config():
    logger.debug("Loading config file...")
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}


def get_vault_credentials():
    logger.debug("Getting vault credentials...")
    config = load_config()
    vault_token = config.get("vault_token")
    vault_role_id = config.get("vault_role_id")
    vault_secret_id = config.get("vault_secret_id")

    return vault_token, vault_role_id, vault_secret_id


def get_session(cert=None, proxies=None):
    logger.info(f"Session created: Cert: {cert}, Proxies: {proxies}")
    session = requests.Session()
    session.trust_env = False
    session.verify = cert if cert else False
    session.proxies = proxies
    return session


def get_vault_addr():
    domain = get_domain()
    if domain == "host1":
        vault_addr = VaultAddr.Host_1
    elif domain == "Host2":
        vault_addr = VaultAddr.Host_2
    elif "runner" in domain:
        domain = os.getenv("CI_SERVER_URL")
        if "." in domain:
            domain = domain.lower().split(".")[1]
            if domain == "host1":
                vault_addr = VaultAddr.Host_1
            elif domain == "host2":
                vault_addr = VaultAddr.Host_2
    else:
        logger.error("Unable to get valid domain for vault.")
        raise VaultManagerError("Unable to get valid domain for vault.")
    logger.info(f"Vault Addr: {vault_addr}")
    return vault_addr


class VaultManagerError(Exception):
    """Custom exception for VaultManager errors."""

    def __init__(self, message: str = "An error occurred in VaultManager."):
        self.message = message
        super().__init__(self.message)


class KeyringManagerError(Exception):
    """Custom exception for KeyringManager errors."""

    def __init__(self, message: str = "An error occurred in KeyringManager."):
        self.message = message
        super().__init__(self.message)
