import datetime

from .BaseQuery import BaseQuery
from .utils import by_epic


class LeadtimeQuery(BaseQuery):
    query_bases = {
        'leadtime': ('PROJECT = {project} '
                     'AND TYPE IN ({types}) '
                     'AND statusCategory = Done '
                     'AND status CHANGED TO Done '
                     'DURING("{begin_date}", "{end_date}")')
    }

    def set_defaults(self):
        if 'types' not in self.vars:
            self.vars['types'] = 'bug, story, task'

    def _get_date(self, date_string):
        return datetime.datetime.strptime(date_string[0:10],
                                          '%Y-%m-%d')

    def _get_issue_lead_time(self, issue):
        created_date = self._get_date(issue.fields.created)
        resolution_date = self._get_date(issue.fields.resolutiondate)
        return (resolution_date - created_date).days

    def _get_issues_lead_time(self, issues):
        total_lead_time = 0
        for issue in issues:
            total_lead_time += self._get_issue_lead_time(issue)
        return total_lead_time / len(issues)

    def build_results(self):
        issues = self.results['leadtime']
        average_lead_time = self._get_issues_lead_time(issues)
        start_date = self.vars['begin_date']
        end_date = self.vars['end_date']
        line = ('Between {begin_date} and {end_date}, '
                'the average lead time was {lead_time} days.')
        self.results_report = line.format(begin_date=start_date,
                                          end_date=end_date,
                                          lead_time=average_lead_time)


class LeadtimebyepicQuery(LeadtimeQuery):
    def build_results(self):
        epics = by_epic(self.results['leadtime'])
        epic_lead_times = {}
        for epic, epic_issues in epics.items():
            epic_lead_times[epic] = self._get_issues_lead_time(epic_issues)

        self.results_report = 'Average lead time (in days) by epic:\n\n'
        epic_line = '\t{epic}: {lead_time} days\n'
        for epic, lead_time in epic_lead_times.items():
            if epic != 'UNASSIGNED':
                self.results_report += epic_line.format(epic=epic,
                                                        lead_time=lead_time)
        unassigned = ('\tAverage lead time for issues not '
                      'assigned to an epic: {lead_time} days')
        unassigned_time = epic_lead_times['UNASSIGNED']
        self.results_report += unassigned.format(lead_time=unassigned_time)
