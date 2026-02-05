import time
import jwt
import ckan.plugins.toolkit as tk
from ckanext.jwt_issuer.services import get_datasets_and_permissions_for_user

def jwt_issuer_token(context, data_dict):
    """
    POST /api/action/jwt_issuer_token
    """
    user = context.get("user")
    if not user:
        tk.abort(401, "Not authenticated")

    secret = tk.config.get("ckanext.jwt_issuer.secret")
    if not secret:
        tk.abort(500, "Missing config: ckanext.jwt_issuer.secret")

    issuer = tk.config.get("ckanext.jwt_issuer.issuer", tk.config.get("ckan.site_url"))
    audience = tk.config.get("ckanext.jwt_issuer.audience", "strapi")
    ttl_default = int(tk.config.get("ckanext.jwt_issuer.ttl_seconds", 600))

    lifetime = ttl_default

    user_datasets_permissions = get_datasets_and_permissions_for_user(user)

    now = int(time.time())
    payload = {
        "iss": issuer,
        "aud": audience,
        "sub": user,
        "iat": now,
        "exp": now + lifetime,
        "permissions": user_datasets_permissions,
    }

    token = jwt.encode(payload, secret, algorithm="HS256")

    return {"token": token, "expires_in": lifetime}

