import ckan.plugins.toolkit as tk

def get_datasets_and_permissions_for_user(username):
    r_list = [] # read ONLY
    w_list = [] # write (+ read)
    context = {'user': username}

    try:
        search_results = tk.get_action('package_search')(context, {
            'include_private': True,
            'rows': 10000 # default is 1000, we want to be sure to get all datasets
        })
    except Exception:
        return {"r": [], "w": []}

    for pkg in search_results.get('results', []):
        pkg_id = pkg['id']
        
        # first test write access
        try:
            if tk.check_access('package_update', context, {'id': pkg_id}):
                w_list.append(pkg_id)
                continue # move to the next dataset, no need to add it to 'r' to avoid duplication
        except tk.NotAuthorized:
            pass

        # if we get here, the user does not have 'w' rights. 
        # but since it is in the search results, they necessarily have 'r' rights.
        r_list.append(pkg_id)

    return {
        "r": r_list,
        "w": w_list
    }