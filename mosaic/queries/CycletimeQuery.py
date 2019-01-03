import datetime
import traceback

from .BaseQuery import BaseQuery
from .utils import date_difference


class CycletimeQuery(BaseQuery):
    supports_rolling = True
    query_bases = {
        'cycletime': ('PROJECT = {project} '
                      'AND TYPE IN ({types}) '
                      'AND statusCategory = Done '
                      'AND status CHANGED TO {end_state} '
                      'DURING("{begin_date}", "{end_date}")'),
        'cycletime_rolling': ('PROJECT = {project} '
                              'AND TYPE IN ({types}) '
                              'AND statusCategory = "In Progress" ')
    }

    def set_defaults(self):
        if 'types' not in self.vars:
            self.vars['types'] = 'bug, story, task'

    def _get_issue_start_date(self, issue):
        start_date = None
        for history in issue.changelog.histories:
            for item in history.items:
                if item.field == 'status':
                    if item.fromString == 'To Do' and item.toString != 'Next':
                        start_date = history.created
                    elif (item.fromString == 'Next' and
                          item.toString != 'To Do'):
                        start_date = history.created
        if start_date is None:
            raise Exception(('No transition from To Do to In Progress '
                             'could be found for issue {0}').format(issue))
        return start_date

    def _get_issue_cycle_time(self, issue):
        start_date = self._get_issue_start_date(issue)
        cycle_time = date_difference(issue.fields.resolutiondate,
                                     start_date)
        line = '\tFor issue {issue}, the cycle time was {cycletime} days'
        self.log.debug(line.format(issue=issue.key, cycletime=cycle_time))
        return cycle_time

    def _get_total_cycle_time(self, issues, in_progress_issues):
        count = len(issues)
        total_cycle_time = 0
        for issue in issues:
            try:
                total_cycle_time += self._get_issue_cycle_time(issue)
            except Exception:
                self.log.debug(traceback.format_exc())
                count -= 1
        if self.rolling:
            self.log.debug(('Calculating time spent so far for in '
                            'progress issues'))
            today = datetime.date.today()
            today = datetime.datetime.strftime(today, '%Y-%m-%d')
            for issue in in_progress_issues:
                start_date = self._get_issue_start_date(issue)
                time_spent = date_difference(today, start_date)
                self.log.debug(('Time spent so far on issue {key}: {duration} '
                                'days.').format(key=issue.key,
                                                duration=time_spent))
                total_cycle_time += time_spent
                count += 1

        if not count:
            return float('nan')
        average_cycle_time = total_cycle_time / count
        return average_cycle_time

    def build_results(self):
        issues = self.results['cycletime']
        in_progress_issues = self.results['cycletime_rolling']
        self.log.debug('There were {0} issues'.format(len(issues)))
        if self.rolling:
            self.log.debug(('Rolling argument specified. Cycle time will be '
                           'calculated using in progress issues'))
            self.log.debug(('There are {len} issues in '
                           'progress.').format(len=len(in_progress_issues)))
        average_cycle_time = self._get_total_cycle_time(issues,
                                                        in_progress_issues)
        self.result = average_cycle_time
        start_date = self.vars['begin_date']
        end_date = self.vars['end_date']
        line = ('Between {begin_date} and {end_date}, '
                'the average cycle time for all issues '
                'was {cycle_time} days.')
        self.results_report = line.format(begin_date=start_date,
                                          end_date=end_date,
                                          cycle_time=average_cycle_time)


class PrioritycycletimeQuery(CycletimeQuery):
    supports_rolling = True
    query_bases = {
        'prioritycycletime': ('PROJECT = {project} '
                              'AND TYPE IN ({types}) '
                              'AND statusCategory = Done '
                              'AND priority in ({argument}) '
                              'AND status CHANGED TO {end_state} '
                              'DURING("{begin_date}", "{end_date}")'),
        'prioritycycletime_rolling': ('PROJECT = {project} '
                                      'AND TYPE IN ({types}) '
                                      'AND statusCategory = "In Progress" '
                                      'AND priority in ({argument}) ')
    }

    def build_results(self):
        issues = self.results['prioritycycletime']
        in_progress_issues = self.results['prioritycycletime_rolling']
        average_cycle_time = self._get_total_cycle_time(issues,
                                                        in_progress_issues)
        self.result = average_cycle_time
        start_date = self.vars['begin_date']
        end_date = self.vars['end_date']
        line = ('Between {begin_date} and {end_date}, '
                'the average cycle time for issues with the '
                '"{priority}" priority '
                'was {cycle_time} days.')
        self.results_report = line.format(begin_date=start_date,
                                          end_date=end_date,
                                          priority=self.vars['argument'],
                                          cycle_time=average_cycle_time)
