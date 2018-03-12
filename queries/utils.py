def by_epic(issues):
    epics = {}
    for issue in issues:
        if hasattr(issue.fields, 'customfield_10006'):
            parent_epic = issue.fields.customfield_10006
            if parent_epic is not None:
                if parent_epic not in epics:
                    epics[parent_epic] = []
                epics[parent_epic].append(issue)
            else:
                if 'UNASSIGNED' not in epics:
                    epics['UNASSIGNED'] = []
                epics['UNASSIGNED'].append(issue)
        else:
            if 'UNASSIGNED' not in epics:
                epics['UNASSIGNED'] = []
            epics['UNASSIGNED'].append(issue)
    return epics
