[![Tests](https://github.com/moxohch/ckanext-jwt_issuer/workflows/Tests/badge.svg?branch=develop)](https://github.com/moxohch/ckanext-jwt_issuer/actions)

## ckanext-jwt_issuer

CKAN extension that exposes an API endpoint to issue short‑lived JSON Web Tokens (JWTs) containing the current user’s dataset permissions.  
The token can be consumed by external applications (for example a CMS like Strapi) to enforce CKAN‑level access control.

The issued JWT includes:

- **iss**: issuer (configured, defaults to CKAN site URL)
- **aud**: audience (configured, defaults to `strapi`)
- **sub**: CKAN username (or `anonymous`)
- **iat / exp**: issued‑at and expiry timestamps
- **r / w**: lists of dataset IDs the user can respectively read (`r`) and write (`w`)


## Requirements

Compatibility with core CKAN versions:

| CKAN version      | Compatible? |
| ----------------- | ---------- |
| 2.11              | yes        |
| 2.10 and earlier  | not tested |


## Installation

### Docker installation

1. Add the extension to your CKAN image, for example in your `Dockerfile`:

   ```bash
   RUN pip3 install --no-cache-dir -e git+https://github.com/moxohch/ckanext-jwt_issuer.git@develop#egg=ckanext-jwt_issuer
   ```

2. Enable the plugin via environment variable:

   ```bash
   CKAN__PLUGINS=jwt_issuer
   ```

   (Make sure you keep other plugins you already use.)

3. Configure the JWT settings via environment variables:

   ```bash
   CKANEXT__JWT_ISSUER__SECRET=change_me_to_a_strong_secret
   CKANEXT__JWT_ISSUER__ISSUER=https://your-ckan.example.org
   CKANEXT__JWT_ISSUER__AUDIENCE=strapi
   CKANEXT__JWT_ISSUER__TTL_SECONDS=600
   ```

4. Rebuild and restart your Docker container.


### Installation without Docker

1. Activate your CKAN virtual environment, for example:

   ```bash
   . /usr/lib/ckan/default/bin/activate
   ```

2. Clone the source and install it in the virtualenv:

   ```bash
   git clone https://github.com/moxohch/ckanext-jwt_issuer.git
   cd ckanext-jwt_issuer
   pip install -e .
   pip install -r requirements.txt
   ```

3. Add `jwt_issuer` to the `ckan.plugins` setting in your CKAN config file (by default located at `/etc/ckan/default/ckan.ini`):

   ```ini
   ckan.plugins = ... jwt_issuer
   ```

4. Configure the JWT settings in your CKAN config file (`ckan.ini`):

   ```ini
   # REQUIRED: secret key used to sign the JWT (HS256)
   ckanext.jwt_issuer.secret = change_me_to_a_strong_secret

   # OPTIONAL: issuer (iss). Defaults to ckan.site_url if not set.
   ckanext.jwt_issuer.issuer = https://your-ckan.example.org

   # OPTIONAL: audience (aud). Defaults to "strapi".
   ckanext.jwt_issuer.audience = strapi

   # OPTIONAL: token lifetime in seconds. Defaults to 600 (10 minutes).
   ckanext.jwt_issuer.ttl_seconds = 600
   ```

5. Restart CKAN. For example, if you use Apache on Ubuntu:

   ```bash
   sudo service apache2 reload
   ```


## Config settings

### `ckanext.jwt_issuer.secret`

- **Required:** yes  
- **Type:** string  
- **Description:** Secret key used to sign JWTs with the HS256 algorithm.  
- **Example (`ckan.ini`):**

  ```ini
  ckanext.jwt_issuer.secret = change_me_to_a_strong_secret
  ```

- **Example (Docker env):**

  ```bash
  CKANEXT__JWT_ISSUER__SECRET=change_me_to_a_strong_secret
  ```


### `ckanext.jwt_issuer.issuer`

- **Required:** no  
- **Type:** string  
- **Default:** value of `ckan.site_url`  
- **Description:** Issuer (`iss` claim) to put into the JWT. Typically the public URL of your CKAN instance.


### `ckanext.jwt_issuer.audience`

- **Required:** no  
- **Type:** string  
- **Default:** `strapi`  
- **Description:** Audience (`aud` claim) for which the token is intended (e.g. a consuming service like Strapi).


### `ckanext.jwt_issuer.ttl_seconds`

- **Required:** no  
- **Type:** integer  
- **Default:** `600` (10 minutes)  
- **Description:** Lifetime of the issued token in seconds (`exp` = `iat` + `ttl_seconds`).


## API endpoint

The extension exposes a single action:

- **Action name:** `jwt_issuer_token`  
- **HTTP endpoint:** `POST /api/action/jwt_issuer_token`  
- **Authentication:** allowed for both logged‑in and anonymous users (the action’s auth function always returns success).  

**Request body**

No specific parameters are required; a minimal request can be:

```bash
curl -X POST "https://your-ckan.example.org/api/action/jwt_issuer_token"
```

**Response example**

```json
{
  "success": true,
  "result": {
    "token": "<jwt_token_here>",
    "expires_in": 600
  }
}
```

When the user is authenticated, the token payload contains:

- `sub`: CKAN username  
- `r`: list of dataset IDs the user can read  
- `w`: list of dataset IDs the user can write (also implies read)  

For anonymous users, `sub` is set to `"anonymous"` and the permission lists are empty.


## Developer installation

To install `ckanext-jwt_issuer` for development, activate your CKAN virtualenv and run:

```bash
git clone https://github.com/moxohch/ckanext-jwt_issuer.git
cd ckanext-jwt_issuer
pip install -e .
pip install -r dev-requirements.txt
```
