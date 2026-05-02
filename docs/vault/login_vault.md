## Logging into Hashicorp Vault UI

**Logging into the UI**

1. In any approved web browser, go to the Vault URL for the environment you are in.

2. At the login screen, select "OIDC" in the Method pulldown menu.

![Screenshot 2024-06-17 101301.png](../img/vault/image6.png)

3. For Role, enter your Gitlab username, and click "Sign in with OIDC Provider".

![image.png](../img/vault/image7.png)

4. When logging in you will be presented with the Secrets Engines you have been granted access to.

![image.png](../img/vault/image8.png)

- The Secrets Engine matching your username, is for your own use, and no other users will have access.
- The Secrets Engine(s) beginning with "group-" are associated with your top-level Gitlab groups. All members of those groups have equal access to that path.
- Cubbyhole is a temporary Secrets Engine, that is only valid for the life of your token, and is used for passing secrets. Do not store any long-term secrets in the cubbyhole.