from .BaseQuery import BaseQuery
from .utils import date_difference


class Transition():
    def __init__(self, to_status, from_status, timestamp):
        self.to_status = to_status
        self.from_status = from_status
        self.timestamp = timestamp


class StatusdurationQuery(BaseQuery):
    template = ('Between {begin_date} and {end_date}, '
                'the average time spent in {qualifier} status '
                'was {value} days.')
    supports_rolling = True

    # This means you can use --rolling in combination with --end-date
    supports_isolated_rolling = True

    query_bases = {
        'statusduration': (
            'PROJECT = {project} '
            'AND TYPE IN ({types}) '
            'AND statusCategory = Done '
            'AND status CHANGED TO {end_state} '
            'DURING("{begin_date}", "{end_date}") '),
        'statusduration_rolling': (
            'PROJECT = {project} '
            'AND TYPE IN ({types}) '
            'AND status CHANGED TO "{argument}" BEFORE "{end_date}" '
            'AND NOT status CHANGED TO {end_state} BEFORE "{begin_date}"'
        ),
    }

    def set_defaults(self):
        if 'types' not in self.vars:
            self.vars['types'] = 'bug, story, task'

    def _get_time_in_status(self, issue, target_status):
        transitions = []
        for history in issue.changelog.histories:
            for item in history.items:
                if item.field == 'status':
                    transitions.append(Transition(
                        item.toString, item.fromString, history.created))

        begin_date, end_date = None, None

        # Try to find the beginning date
        # XXX - use `reversed(transitions)` here for a more generous result
        for transition in transitions:
            if transition.to_status == target_status:
                self.log.debug(('Found a transition into the status '
                                '"{status}" for issue '
                                '{key}"').format(status=transition.to_status,
                                                 key=issue.key))
                begin_date = transition.timestamp
                break

        if not begin_date:
            # If we get here, the issue never entered the target status
            self.log.debug(('Issue {key} never entered the "{status}" '
                            'status.').format(key=issue.key,
                                              status=target_status))
            return -1

        # Try to find the end date
        for transition in reversed(transitions):
            if transition.from_status == target_status:
                self.log.debug(('Found a transition out of the status '
                                '"{status}" for issue '
                                '{key}"').format(status=transition.from_status,
                                                 key=issue.key))
                end_date = transition.timestamp
                break

        # If the item is still in the target state, then use the end of the
        # query period.
        if not end_date:
            end_date = self.vars['end_date']

        duration = date_difference(end_date, begin_date)
        return duration

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
        self.log.debug(('{count} total issues entered the target '
                        'state').format(count=issues))
        if not issues:
            average_duration = float('nan')
        else:
            average_duration = total_duration / issues

        self.result = average_duration
        self.results_report = [dict(
            begin_date=start_date,
            end_date=end_date,
            qualifier=target_status,
            value=average_duration,
        )]
