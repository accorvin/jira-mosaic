from .BaseQuery import BaseQuery
from .utils import by_epic, date_difference


class LeadtimeQuery(BaseQuery):
    template = ('Between {begin_date} and {end_date}, '
                'the average lead time was {value} days.')
    query_bases = {
        'leadtime': ('PROJECT = {project} '
                     'AND TYPE IN ({types}) '
                     'AND statusCategory = Done '
                     'AND status CHANGED TO {end_state} '
                     'DURING("{begin_date}", "{end_date}")')
    }

    def set_defaults(self):
        if 'types' not in self.vars:
            self.vars['types'] = 'bug, story, task'

    def _get_issue_lead_time(self, issue):
        lead_time = date_difference(
            issue.fields.resolutiondate, issue.fields.created,
            self.vars['epoch'])
        line = '\tFor issue {issue}, the lead time was {leadtime} days'
        self.log.debug(line.format(issue=issue.key, leadtime=lead_time))
        return lead_time

    def _get_issues_lead_time(self, issues):
        total_lead_time = 0
        for issue in issues:
            total_lead_time += self._get_issue_lead_time(issue)
        if not issues:
            return float('nan'), 0
        return total_lead_time / len(issues), len(issues)

    def build_results(self):
        issues = self.results['leadtime']
        average_lead_time, count = self._get_issues_lead_time(issues)
        self.result = average_lead_time
        start_date = self.vars['begin_date']
        end_date = self.vars['end_date']
        self.results_report = [dict(
            begin_date=start_date,
            end_date=end_date,
            value=average_lead_time,
            count=count,
        )]


class LeadtimebyepicQuery(LeadtimeQuery):
    template = ('Between {begin_date} and {end_date}, '
                'the average lead time for {qualifier} was {value} days.')

    def build_results(self):
        epics = by_epic(self.results['leadtime'])
        epic_lead_times = {}
        for epic, epic_issues in epics.items():
            epic_lead_times[epic] = self._get_issues_lead_time(epic_issues)

        start_date = self.vars['begin_date']
        end_date = self.vars['end_date']
        self.results_report = [dict(
            begin_date=start_date,
            end_date=end_date,
            qualifier=epic,
            value=values[0],
            count=values[1],
        ) for epic, values in epic_lead_times.items()]
