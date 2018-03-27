from .BaseQuery import BaseQuery
from .utils import date_difference


class Transition():
    def __init__(self, status, timestamp):
        self.status = status
        self.timestamp = timestamp


class StatusdurationQuery(BaseQuery):
    query_bases = {
        'statusduration': ('PROJECT = {project} '
                           'AND TYPE IN ({types}) '
                           'AND statusCategory = Done '
                           'AND status CHANGED TO Done '
                           'DURING("{begin_date}", "{end_date}") ')
    }

    def set_defaults(self):
        if 'types' not in self.vars:
            self.vars['types'] = 'bug, story, task'

    def _get_time_in_status(self, issue, status):
        transitions = []
        for history in issue.changelog.histories:
            for item in history.items:
                if item.field == 'status':
                    status = item.fromString
                    timestamp = history.created
                    transitions.append(Transition(status, timestamp))

        for index, transition in enumerate(transitions):
            if transition.status == status:
                if index == 0:
                    begin_date = issue.fields.created
                end_date = transition.timestamp
                begin_date = transitions[index - 1].timestamp
                duration = date_difference(end_date, begin_date)
                return duration

        # If we get this far, the issue never entered the target status
        return -1

    def build_results(self):
        target_status = self.vars['argument']
        issues = len(self.results['statusduration'])
        total_duration = 0
        for issue in self.results['statusduration']:
            duration = self._get_time_in_status(issue, target_status)
            if duration < 0:
                issues = issues - 1
            else:
                total_duration += duration

        average_duration = total_duration / issues
        start_date = self.vars['begin_date']
        end_date = self.vars['end_date']
        line = ('Between {begin_date} and {end_date}, '
                'the average time spent in {status} status '
                'was {duration} days.')
        self.results_report = line.format(begin_date=start_date,
                                          end_date=end_date,
                                          status=target_status,
                                          duration=average_duration)
