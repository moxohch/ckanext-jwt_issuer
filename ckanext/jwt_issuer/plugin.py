import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckanext.jwt_issuer import actions



class JwtIssuerPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IActions)
    

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, "templates")
        toolkit.add_public_directory(config_, "public")
        toolkit.add_resource("assets", "jwt_issuer")

    def get_actions(self):
        return {
            "jwt_issuer_token": actions.jwt_issuer_token,
        }

    
