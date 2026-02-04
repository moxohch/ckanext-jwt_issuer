import ckan.plugins.toolkit as tk


def get_organisations_and_roles_for_user(username):
    
    # get organizations the user belongs to
    user_orgs = tk.get_action('organization_list_for_user')(
        {'user': username}, 
    )
    
    orgs_payload = {}
    for org in user_orgs:
        orgs_payload[org['name']] = org['capacity']
        
    return orgs_payload