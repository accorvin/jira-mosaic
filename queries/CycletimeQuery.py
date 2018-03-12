import datetime

from .BaseQuery import BaseQuery


class CycletimeQuery(BaseQuery):
    query_bases = {
        'cycletime': ('PROJECT = {project} '
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

    def _get_issue_cycle_time(self, issue):
        in_progress_date = None
        for history in issue.changelog.histories:
            for item in history.items:
                if (item.field == 'status' and item.fromString == 'Next' and
                        item.toString == 'In Progress'):
                    in_progress_date = history.created
        if in_progress_date is None:
            raise Exception(('No transition from To Do to In Progress '
                             'could be found for issue {0}').format(issue))

        in_progress_date = self._get_date(in_progress_date)
        resolution_date = self._get_date(issue.fields.resolutiondate)
        return (resolution_date - in_progress_date).days

    def build_results(self):
        issues = len(self.results['cycletime'])
        total_cycle_time = 0
        for issue in self.results['cycletime']:
            try:
                total_cycle_time += self._get_issue_cycle_time(issue)
            except Exception:
                issues = issues - 1

        average_cycle_time = total_cycle_time / issues
        start_date = self.vars['begin_date']
        end_date = self.vars['end_date']
        line = ('Between {begin_date} and {end_date}, '
                'the average cycle time was {cycle_time} days.')
        self.results_report = line.format(begin_date=start_date,
                                          end_date=end_date,
                                          cycle_time=average_cycle_time)
