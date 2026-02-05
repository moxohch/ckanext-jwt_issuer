import ckan.plugins.toolkit as tk

def get_datasets_and_permissions_for_user(username):
    """
    returns dict { dataset_id: ["read", "write"] }
    includes all public datasets (read) and organization datasets (read/write).
    """
    datasets_payload = {}
    context = {'user': username}

    # Retrieve all datasets the user can see (public + their private)
    try:
        search_results = tk.get_action('package_search')(context, {
            'include_private': True,
        })
    except Exception:
        return {}

    for pkg in search_results.get('results', []):
        pkg_id = pkg['id']
        # By default, if the dataset appears here, the user has at least 'read' permission
        permissions = ['r']

        # Check if the user has the right to modify the package, which means they are at least editor
        try:
            can_update = tk.check_access('package_update', context, {'id': pkg_id})
            if can_update:
                permissions.append('w')
        except tk.NotAuthorized:
            pass

        datasets_payload[pkg_id] = permissions

    return datasets_payload