import datetime


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


def date_difference(later_date, earlier_date):
    date_format = '%Y-%m-%d'
    later_date = later_date[0:10]
    earlier_date = earlier_date[0:10]
    later_date_object = datetime.datetime.strptime(later_date,
                                                   date_format)
    earlier_date_object = datetime.datetime.strptime(earlier_date,
                                                     date_format)
    difference = (later_date_object - earlier_date_object).days
    return difference
