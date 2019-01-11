from .BaseQuery import BaseQuery
from .utils import by_epic


class ThroughputQuery(BaseQuery):
    template = ('Between {begin_date} and {end_date}, '
                '{value} issues transitioned to the Done state.')
    query_bases = {
        'throughput': ('PROJECT = {project} '
                       'AND TYPE IN ({types}) '
                       'AND statusCategory = Done '
                       'AND status CHANGED TO {end_state} '
                       'DURING("{begin_date}", "{end_date}")')
    }

    def build_results(self):
        result_count = len(self.results['throughput'])
        self.result = result_count
        start_date = self.vars['begin_date']
        end_date = self.vars['end_date']
        self.results_report = [dict(
            begin_date=start_date,
            end_date=end_date,
            value=result_count,
            count=result_count,
        )]


class ThroughputbyepicQuery(ThroughputQuery):
    template = ('Between {begin_date} and {end_date}, '
                '{value} issues transitioned to the Done state '
                'on the {qualifier} epic.')

    def build_results(self):
        epics = by_epic(self.results['throughput'])

        epic_throughput = {}
        for epic, epic_issues in epics.items():
            epic_throughput[epic] = len(epic_issues)

        unassigned_issues_list = [issue.key for issue in epics['UNASSIGNED']]
        unassigned_issues = ', '.join(unassigned_issues_list)
        msg = 'The following issues were not assigned to an epic: {0}'
        self.log.debug(msg.format(unassigned_issues))

        start_date = self.vars['begin_date']
        end_date = self.vars['end_date']
        self.results_report = [dict(
            begin_date=start_date,
            end_date=end_date,
            value=throughput,
            count=throughput,
            qualifier=epic,
        ) for epic, throughput in epic_throughput.items()]
