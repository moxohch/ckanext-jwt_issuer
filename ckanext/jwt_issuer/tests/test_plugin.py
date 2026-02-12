import pytest
import jwt
from ckan import model
from ckan.plugins import toolkit
from ckan.tests import factories

@pytest.mark.ckan_config("ckan.plugins", "jwt_issuer")
@pytest.mark.ckan_config("ckanext.jwt_issuer.secret", "test-secret")
@pytest.mark.ckan_config("ckanext.jwt_issuer.audience", "strapi")
@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestJWTIssuerLogic:
    
    def _decode(self, token):
        return jwt.decode(token, "test-secret", algorithms=["HS256"], audience="strapi")

    def test_logic_anonymous(self):
        org = factories.Organization()
        pub_ds = factories.Dataset(owner_org=org["id"], private=False) 
        priv_ds = factories.Dataset(owner_org=org["id"], private=True)

        # no user
        context = {'user': None, 'model': model, 'session': model.Session}
        
        result = toolkit.get_action("jwt_issuer_token")(context, {})
        
        decoded = self._decode(result["token"])
        assert decoded["sub"] == "anonymous"
        assert "r" in decoded
        assert "w" in decoded

        assert pub_ds["id"] in decoded["r"]
        assert pub_ds["id"] not in decoded["w"]

        assert priv_ds["id"] not in decoded["r"]
        assert priv_ds["id"] not in decoded["w"]

        # no dataset should be in both 'r' and 'w'
        assert set(decoded["r"]).isdisjoint(set(decoded["w"]))

    def test_logic_org_admin(self):
        user = factories.User()
        org = factories.Organization(users=[{"name": user["name"], "capacity": "admin"}])
        dataset = factories.Dataset(owner_org=org["id"], private=True)

        # On appelle l'action en passant simplement le nom de l'utilisateur
        context = {
            'user': user['name'], 
            'model': model, 
            'session': model.Session
        }
        
        result = toolkit.get_action("jwt_issuer_token")(context, {})
        decoded = self._decode(result["token"])

        assert decoded["sub"] == user["name"]
        assert dataset["id"] in decoded["w"]

        assert dataset["id"] not in decoded["r"]
        
        # no dataset should be in both 'r' and 'w'
        assert set(decoded["r"]).isdisjoint(set(decoded["w"]))

    def test_logic_other_user_only_read(self):
        admin = factories.User()
        org = factories.Organization(users=[{"name": admin["name"], "capacity": "admin"}])
        
        pub_ds = factories.Dataset(owner_org=org["id"], private=False)
        priv_ds = factories.Dataset(owner_org=org["id"], private=True)

        # test with another user who is not a member of the org, should only have 'r' for the public dataset
        visitor = factories.User()
        context = {'user': visitor['name'], 'model': model, 'session': model.Session}
        
        result = toolkit.get_action("jwt_issuer_token")(context, {})
        decoded = self._decode(result["token"])

        assert pub_ds["id"] in decoded["r"]
        assert pub_ds["id"] not in decoded["w"]
        assert priv_ds["id"] not in decoded["r"]
        assert priv_ds["id"] not in decoded["w"]

        # no dataset should be in both 'r' and 'w'
        assert set(decoded["r"]).isdisjoint(set(decoded["w"]))
