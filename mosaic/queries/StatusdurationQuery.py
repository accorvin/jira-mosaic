import datetime

from .BaseQuery import BaseQuery
from .utils import date_difference


class Transition():
    def __init__(self, status, timestamp):
        self.status = status
        self.timestamp = timestamp


class StatusdurationQuery(BaseQuery):
    supports_rolling = True
    query_bases = {
        'statusduration': ('PROJECT = {project} '
                           'AND TYPE IN ({types}) '
                           'AND statusCategory = Done '
                           'AND status CHANGED TO Done '
                           'DURING("{begin_date}", "{end_date}") '),
        'statusduration_rolling': ('PROJECT = {project} '
                                   'AND TYPE IN ({types}) '
                                   'AND statusCategory = "In Progress" ')
    }

    def set_defaults(self):
        if 'types' not in self.vars:
            self.vars['types'] = 'bug, story, task'

    def _get_time_in_status(self, issue, target_status):
        transitions = []
        for history in issue.changelog.histories:
            for item in history.items:
                if item.field == 'status':
                    status = item.toString
                    timestamp = history.created
                    transitions.append(Transition(status, timestamp))

        for index, transition in enumerate(transitions):
            if transition.status == target_status:
                self.log.debug(('Found a transition into the status '
                                '"{status}" for issue '
                                '{key}"').format(status=status,
                                                 key=issue.key))
                if index == 0:
                    begin_date = issue.fields.created
                # if an issue is in progress, that means the --rolling
                # argument was specified and we want to get the number
                # of days so far that the issue has spent in the target
                # status, so the end date should be today and the begin
                # date should be the date that the issue entered the current
                # status
                if issue.fields.status.name != 'Done':
                    today = datetime.date.today()
                    end_date = datetime.datetime.strftime(today, '%Y-%m-%d')
                    begin_date = transition.timestamp
                else:
                    begin_date = transition.timestamp
                    if index == len(transitions) - 1:
                        end_date = issue.fields.resolutiondate
                    else:
                        end_date = transitions[index + 1].timestamp
                duration = date_difference(end_date, begin_date)
                return duration

        # If we get this far, the issue never entered the target status
        self.log.debug(('Issue {key} never entered the "{status}" '
                        'status.').format(key=issue.key,
                                          status=target_status))
        return -1

    def build_results(self):
        target_status = self.vars['argument']
        issues = len(self.results['statusduration'])
        in_progress_issues = self.results['statusduration_rolling']
        self.log.debug(('{len} issues were completed during the target '
                        'date range.').format(len=issues))
        total_duration = 0
        for issue in self.results['statusduration']:
            duration = self._get_time_in_status(issue, target_status)
            if duration < 0:
                issues = issues - 1
            else:
                self.log.debug(('Time spent in status "{status}" for issue '
                                '"{key}: {duration} '
                                'days').format(status=target_status,
                                               key=issue.key,
                                               duration=duration))
                total_duration += duration
        if self.rolling:
            self.log.debug(('Rolling argument specified. Issues in progress '
                            'will be used to calculate status duration.'))
            self.log.debug(('{len} issues are currently in '
                            'progress.').format(len=len(in_progress_issues)))
            for issue in in_progress_issues:
                duration = self._get_time_in_status(issue, target_status)
                if duration >= 0:
                    self.log.debug(('Time spent in status "{status}" for '
                                    'issue "{key}: {duration} '
                                    'days').format(status=target_status,
                                                   key=issue.key,
                                                   duration=duration))
                    total_duration += duration
                    issues += 1

        start_date = self.vars['begin_date']
        end_date = self.vars['end_date']
        if issues == 0:
            line = ('No issues entered the "{status}" state during the time '
                    'period beginning on {begin_date} and ending on '
                    '{end_date}')
            self.results_report = line.format(status=target_status,
                                              begin_date=start_date,
                                              end_date=end_date)
        else:
            self.log.debug(('{count} total issues entered the target '
                            'state').format(count=issues))
            average_duration = total_duration / issues
            self.result = average_duration
            line = ('Between {begin_date} and {end_date}, '
                    'the average time spent in {status} status '
                    'was {duration} days.')
            self.results_report = line.format(begin_date=start_date,
                                              end_date=end_date,
                                              status=target_status,
                                              duration=average_duration)
