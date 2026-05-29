"""HashiCorp Vault backend for credential-bridge."""

import getpass
import os
from contextlib import contextmanager
from typing import Any, Dict, Generator, List, Optional, Tuple, Union

import hvac
import requests
from pylogshield import LogLevel, PyLogShield, get_logger

from ..exceptions import (
    ConfigurationError,
    VaultAuthError,
    VaultConnectionError,
    VaultError,
    VaultSecretNotFoundError,
)
from ..utils import load_config, save_config
from .base import BaseSecretBackend


def _safe_getuser() -> str:
    """Return the current OS username, cross-platform safe.

    getpass.getuser() falls back to the pwd module when no username env var is
    set; pwd does not exist on Windows, so we catch any failure and try the
    standard env vars manually before giving up.
    """
    try:
        return getpass.getuser()
    except (ModuleNotFoundError, KeyError, OSError):
        return os.environ.get("USERNAME") or os.environ.get("USER") or os.environ.get("LOGNAME") or "default"


class VaultBackend(BaseSecretBackend):
    """HashiCorp Vault KV-v2 secret backend."""

    backend_name: str = "vault"

    def __init__(
        self,
        vault_url: Optional[str] = None,
        vault_token: Optional[str] = None,
        vault_role_id: Optional[str] = None,
        vault_secret_id: Optional[str] = None,
        service_name: str = "default_service",
        mount_point: Optional[str] = None,
        proxies: Optional[Dict[str, str]] = None,
        cert: Optional[str] = None,
        tls_client_cert: Optional[Tuple[str, str]] = None,
        namespace: Optional[str] = None,
        timeout: int = 30,
        allow_redirects: bool = True,
        session: Optional[requests.Session] = None,
        log_level: Union[LogLevel, str] = LogLevel.WARNING,
        logger: Optional[PyLogShield] = None,
        mask: bool = True,
        persist: bool = False,
    ) -> None:
        """Create a VaultBackend instance and authenticate with Vault.

        Address resolution order: ``vault_url`` → ``VAULT_ADDR`` env var →
        ``vault_addr`` in ``~/.vault_config.json`` → ``ConfigurationError``.
        This check runs first, before any other setup (fail-fast).

        Parameters
        ----------
        vault_url : str, optional
            Vault server base URL. If omitted, ``VAULT_ADDR`` and then
            ``~/.vault_config.json`` are consulted.
        vault_token : str, optional
            Token for token-based auth. Mutually exclusive with ``vault_role_id``
            / ``vault_secret_id``. Falls back to ``vault_token`` in
            ``~/.vault_config.json`` when omitted.
        vault_role_id : str, optional
            AppRole role ID. Must be combined with ``vault_secret_id``.
        vault_secret_id : str, optional
            AppRole secret ID. Must be combined with ``vault_role_id``.
        service_name : str
            Logging tag. Not used in any Vault API call.
        mount_point : str, optional
            KV-v2 engine mount point. Defaults to the current OS username via
            ``getpass.getuser()`` (cross-platform safe on Windows).
        proxies : dict, optional
            Proxy map forwarded to ``hvac.Client`` (e.g.
            ``{"https": "http://proxy:8080"}``).
        cert : str, optional
            Path to a CA bundle for TLS server verification, forwarded as
            ``verify=`` to ``hvac.Client``. ``None`` uses the system CA bundle.
            TLS verification cannot be disabled.
        tls_client_cert : tuple, optional
            ``(cert_path, key_path)`` tuple for mutual TLS, forwarded as
            ``cert=`` to ``hvac.Client``.
        namespace : str, optional
            Vault Enterprise namespace (e.g. ``"team-a/"``). Forwarded to
            ``hvac.Client``. Leave ``None`` for open-source Vault.
        timeout : int
            Request timeout in seconds forwarded to ``hvac.Client``. Defaults
            to 30 (the hvac default).
        allow_redirects : bool
            Whether to follow HTTP redirects, forwarded to ``hvac.Client``.
        session : requests.Session, optional
            Pre-configured ``requests.Session`` forwarded to ``hvac.Client``.
            When provided, the session's own ``verify``, ``cert``, and
            ``proxies`` settings take effect and the constructor-level values
            for those parameters are ignored by requests.
        log_level : LogLevel or str
            Minimum log level for the internal ``PyLogShield`` logger.
        logger : PyLogShield, optional
            Bring-your-own logger. Must be a ``PyLogShield`` instance.
        mask : bool
            Mask secret values in log output.
        persist : bool
            Write the resolved address and credentials to
            ``~/.vault_config.json`` so future ``VaultBackend()`` calls with no
            arguments can authenticate without repeating them. Defaults to
            ``False``.
        """
        # --- Fail fast: resolve vault address before any other setup ---
        config = load_config()
        if vault_url:
            self.vault_addr = vault_url
        else:
            self.vault_addr = os.environ.get("VAULT_ADDR") or config.get("vault_addr")  # type: ignore[assignment]

        if not self.vault_addr:
            raise ConfigurationError(
                "Vault address must be provided via the vault_url argument, "
                "the VAULT_ADDR environment variable, or ~/.vault_config.json"
            )

        self.mask = mask
        self.service_name = service_name
        self.mount_point = mount_point if mount_point is not None else _safe_getuser()
        self.cert = cert  # CA bundle path passed as verify= to hvac; None uses system CA bundle
        self.tls_client_cert = tls_client_cert  # (cert_path, key_path) tuple for mutual TLS
        self.namespace = namespace
        self.timeout = timeout
        self.allow_redirects = allow_redirects
        self.session = session
        self.proxies = proxies

        if logger and not isinstance(logger, PyLogShield):
            raise ConfigurationError("logger must be a PyLogShield instance. Use: from pylogshield import PyLogShield")
        self.logger = logger or get_logger(name="credential_bridge", log_level=log_level, force=True)

        # --- Resolve credentials (args override config) ---
        # Stored under underscore-prefixed names to keep the secret material off
        # the public attribute surface (vault_addr / mount_point remain public).
        self._vault_token = vault_token if vault_token is not None else config.get("vault_token")
        self._vault_role_id = vault_role_id if vault_role_id is not None else config.get("vault_role_id")
        self._vault_secret_id = vault_secret_id if vault_secret_id is not None else config.get("vault_secret_id")

        # Token and AppRole are mutually exclusive
        if self._vault_token and (self._vault_role_id or self._vault_secret_id):
            raise ConfigurationError("Provide either a Vault token or AppRole credentials, not both.")

        # At least one auth method must be present
        if not self._vault_token and not (self._vault_role_id and self._vault_secret_id):
            raise ConfigurationError(
                "No authentication method provided. Please provide either a token or AppRole credentials."
            )

        # --- Persist credentials to config (opt-in) ---
        if persist:
            if self._vault_token:
                config["vault_token"] = self._vault_token
                config["vault_role_id"] = None
                config["vault_secret_id"] = None
            elif self._vault_role_id and self._vault_secret_id:
                config["vault_role_id"] = self._vault_role_id
                config["vault_secret_id"] = self._vault_secret_id
                config["vault_token"] = None

            config["vault_addr"] = self.vault_addr

            save_config(config)

        self.client = self._authenticate()

    def __repr__(self) -> str:
        auth = "token" if self._vault_token else "approle"
        return f"VaultBackend(vault_addr={self.vault_addr!r}, auth={auth!r}, mount_point={self.mount_point!r})"

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------

    def _authenticate(self) -> hvac.Client:
        """Authenticate with Vault using a token or AppRole credentials."""
        self.logger.info("Authenticating with Vault...")
        try:
            tls_verify = self.cert if self.cert is not None else True
            # When no session is supplied, create one with trust_env=False so
            # that ambient HTTP_PROXY / HTTPS_PROXY env vars do not silently
            # route Vault traffic through an unintended proxy.
            effective_session = self.session
            if effective_session is None:
                effective_session = requests.Session()
                effective_session.trust_env = False
            shared_kwargs: Dict[str, Any] = {
                "url": self.vault_addr,
                "verify": tls_verify,
                "proxies": self.proxies,
                "timeout": self.timeout,
                "namespace": self.namespace,
                "cert": self.tls_client_cert,
                "allow_redirects": self.allow_redirects,
                "session": effective_session,
            }
            if self._vault_token:
                client = hvac.Client(**shared_kwargs, token=self._vault_token)
                if not client.is_authenticated():
                    raise VaultAuthError("Failed to authenticate with Vault using token.")
                self.logger.info("Authenticated with Vault via token.")
                return client

            # AppRole
            client = hvac.Client(**shared_kwargs)
            auth_response = client.auth.approle.login(
                role_id=self._vault_role_id,
                secret_id=self._vault_secret_id,
            )
            if "auth" not in auth_response or "client_token" not in auth_response["auth"]:
                raise VaultAuthError("Failed to authenticate with Vault using AppRole.")
            client.token = auth_response["auth"]["client_token"]
            self.logger.info("Authenticated with Vault via AppRole.")
            return client

        except VaultAuthError:
            raise
        except VaultConnectionError:
            raise
        except hvac.exceptions.Forbidden as exc:
            raise VaultAuthError(f"Forbidden: {exc}") from exc
        except hvac.exceptions.InvalidRequest as exc:
            raise VaultAuthError(f"Invalid request: {exc}") from exc
        except (hvac.exceptions.VaultDown, requests.ConnectionError, requests.Timeout) as exc:
            raise VaultConnectionError(f"Cannot connect to Vault at {self.vault_addr}: {exc}") from exc
        except (ConnectionError, OSError) as exc:
            raise VaultConnectionError(f"Cannot reach Vault at {self.vault_addr}: {exc}") from exc
        except Exception as exc:
            raise VaultError(f"Vault authentication error: {exc}") from exc

    def _refresh_token_if_needed(self) -> None:
        """Renew the Vault token if its TTL is below 5 minutes; re-auth for expired AppRole tokens."""
        try:
            resp = self.client.auth.token.lookup_self()
            if resp["data"]["ttl"] < 300:
                self.client.auth.token.renew_self()
                self.logger.info("Vault token refreshed.")
        except hvac.exceptions.Forbidden as e:
            if self._vault_role_id and self._vault_secret_id:
                self.logger.info("AppRole token expired, re-authenticating...")
                self.client = self._authenticate()
            else:
                raise VaultAuthError(f"Vault token is invalid or has expired: {e}") from e
        except (hvac.exceptions.VaultDown, requests.ConnectionError, requests.Timeout, ConnectionError, OSError) as e:
            raise VaultConnectionError(f"Cannot reach Vault at {self.vault_addr}: {e}") from e
        except VaultAuthError:
            raise
        except Exception as e:
            # Broad catch is intentional: we don't want a transient lookup
            # failure to break the actual user operation that follows. Include
            # the exception type so the next op's failure (if any) is easier
            # to correlate back to this swallowed error.
            self.logger.warning(
                "Token refresh check failed (%s: %s); will retry on next operation.",
                type(e).__name__,
                e,
            )

    # ------------------------------------------------------------------
    # Exception mapping context manager
    # ------------------------------------------------------------------

    @contextmanager
    def _vault_call(self, operation: str, name: str = "") -> Generator[None, None, None]:
        """Map common Vault / network exceptions to credential-bridge exceptions."""
        try:
            yield
        except (VaultAuthError, VaultConnectionError, VaultSecretNotFoundError, VaultError):
            raise
        except hvac.exceptions.InvalidPath as exc:
            path_desc = f"Secret path '{name}' does not exist" if name else "Secret path not found"
            raise VaultSecretNotFoundError(f"{path_desc}: {exc}") from exc
        except (hvac.exceptions.VaultDown, requests.ConnectionError, requests.Timeout) as exc:
            raise VaultConnectionError(f"Cannot reach Vault at {self.vault_addr}: {exc}") from exc
        except (ConnectionError, OSError) as exc:
            raise VaultConnectionError(f"Cannot reach Vault at {self.vault_addr}: {exc}") from exc
        except Exception as exc:
            raise VaultError(f"{operation}: {exc}") from exc

    # ------------------------------------------------------------------
    # BaseSecretBackend interface
    # ------------------------------------------------------------------

    def add_secret(self, name: str, secret: Dict[str, Any]) -> None:
        """Add or update a secret in Vault (creates a new KV-v2 version)."""
        self._refresh_token_if_needed()
        with self._vault_call(f"Failed to add secret '{name}'", name=name):
            self.client.secrets.kv.v2.create_or_update_secret(
                path=name,
                secret=secret,
                mount_point=self.mount_point,
            )
        self.logger.info(f"Secret added: {name}")

    def get_secret(self, name: str) -> Dict[str, Any]:
        """Retrieve a secret by *name*."""
        self._refresh_token_if_needed()
        with self._vault_call(f"Failed to get secret '{name}'", name=name):
            response = self.client.secrets.kv.v2.read_secret(
                path=name,
                mount_point=self.mount_point,
            )
            data = response["data"]["data"]
            if data is None:
                raise VaultSecretNotFoundError(
                    f"Secret '{name}' is soft-deleted. Restore it with undelete_secret_versions() first."
                )
        return data  # type: ignore[no-any-return]

    def update_secret(self, name: str, secret: Dict[str, Any]) -> None:
        """Update an existing secret."""
        self._refresh_token_if_needed()
        with self._vault_call(f"Failed to update secret '{name}'", name=name):
            self.client.secrets.kv.v2.patch(
                path=name,
                secret=secret,
                mount_point=self.mount_point,
            )
        self.logger.info(f"Secret updated: {name}")

    def delete_secret(self, name: str) -> None:
        """Permanently delete a secret and all its versions."""
        self._refresh_token_if_needed()
        with self._vault_call(f"Failed to delete secret '{name}'", name=name):
            self.client.secrets.kv.v2.delete_metadata_and_all_versions(
                path=name,
                mount_point=self.mount_point,
            )
        self.logger.info(f"Secret deleted: {name}")

    def list_secrets(self, path: str = "") -> List[str]:
        """List secret keys under *path*."""
        self._refresh_token_if_needed()
        with self._vault_call(f"Failed to list secrets at '{path}'"):
            response = self.client.secrets.kv.v2.list_secrets(
                path=path,
                mount_point=self.mount_point,
            )
            return response["data"]["keys"]  # type: ignore[no-any-return]

    # ------------------------------------------------------------------
    # Extra helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _mask(val: str) -> str:
        """Return a masked version of *val* safe for logging or repr."""
        return val[:4] + "***" if len(val) > 4 else "***"

    def get_vault_creds(self) -> Dict[str, str]:
        """Return the credentials in use by this backend instance (values are masked)."""
        creds: Dict[str, str] = {}
        if self._vault_token:
            creds["vault_token"] = self._mask(self._vault_token)
        if self._vault_role_id:
            creds["vault_role_id"] = self._mask(self._vault_role_id)
        if self._vault_secret_id:
            creds["vault_secret_id"] = self._mask(self._vault_secret_id)
        return creds

    def get_config(self) -> Optional[Dict[str, Any]]:
        """Return the KV engine configuration for the current mount point."""
        self._refresh_token_if_needed()
        with self._vault_call(f"Failed to read config for mount '{self.mount_point}'"):
            return self.client.secrets.kv.v2.read_configuration(mount_point=self.mount_point)  # type: ignore[no-any-return]

    def read_secret_metadata(self, name: str) -> Optional[Dict[str, Any]]:
        """Return metadata and version info for *name*."""
        self._refresh_token_if_needed()
        with self._vault_call(f"Failed to read metadata for '{name}'", name=name):
            return self.client.secrets.kv.v2.read_secret_metadata(  # type: ignore[no-any-return]
                path=name,
                mount_point=self.mount_point,
            )

    def delete_secret_versions(self, name: str, versions: List[int]) -> None:
        """Soft-delete specific versions of *name*."""
        self._refresh_token_if_needed()
        with self._vault_call(f"Failed to delete versions {versions} of '{name}'"):
            self.client.secrets.kv.v2.delete_secret_versions(
                path=name,
                versions=versions,
                mount_point=self.mount_point,
            )
        self.logger.info(f"Soft-deleted versions {versions} of '{name}'.")

    def undelete_secret_versions(self, name: str, versions: List[int]) -> None:
        """Restore soft-deleted versions of *name*."""
        self._refresh_token_if_needed()
        with self._vault_call(f"Failed to undelete versions {versions} of '{name}'"):
            self.client.secrets.kv.v2.undelete_secret_versions(
                path=name,
                versions=versions,
                mount_point=self.mount_point,
            )
        self.logger.info(f"Undeleted versions {versions} of '{name}'.")

    def destroy_secret_versions(self, name: str, versions: List[int]) -> None:
        """Permanently destroy specific versions of *name*."""
        self._refresh_token_if_needed()
        with self._vault_call(f"Failed to destroy versions {versions} of '{name}'"):
            self.client.secrets.kv.v2.destroy_secret_versions(
                path=name,
                versions=versions,
                mount_point=self.mount_point,
            )
        self.logger.info(f"Destroyed versions {versions} of '{name}'.")
