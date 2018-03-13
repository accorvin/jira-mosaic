from .BaseQuery import BaseQuery
from .utils import by_epic


class ThroughputQuery(BaseQuery):
    query_bases = {
        'throughput': ('PROJECT = {project} '
                       'AND TYPE IN ({types}) '
                       'AND statusCategory = Done '
                       'AND status CHANGED TO Done '
                       'DURING("{begin_date}", "{end_date}")')
    }

    def set_defaults(self):
        if 'types' not in self.vars:
            self.vars['types'] = 'bug, story, task'

    def build_results(self):
        result_count = len(self.results['throughput'])
        start_date = self.vars['begin_date']
        end_date = self.vars['end_date']
        line = ('Between {begin_date} and {end_date}, '
                '{count} issues transitioned to the Done state.')
        self.results_report = line.format(begin_date=start_date,
                                          end_date=end_date,
                                          count=result_count)


class ThroughputbyepicQuery(ThroughputQuery):
    def build_results(self):
        epics = by_epic(self.results['throughput'])

        epic_throughput = {}
        for epic, epic_issues in epics.items():
            epic_throughput[epic] = len(epic_issues)

        self.results_report = 'Number of issues completed by epic:\n\n'
        epic_line = '\t{epic}: {throughput} issues\n'
        for epic, throughput in epic_throughput.items():
            if epic != 'UNASSIGNED':
                self.results_report += epic_line.format(epic=epic,
                                                        throughput=throughput)

        # Count everything assigned
        assigned = ('\tCount of issues assigned to an epic: '
                    '{throughput}\n')
        assigned_items = sum([
            throughput for epic, throughput in epic_throughput.items()
            if epic != 'UNASSIGNED'
        ])
        self.results_report += assigned.format(throughput=assigned_items)

        # Count everything unassigned
        unassigned = ('\tCount of issues not assigned to an epic: '
                      '{throughput}')
        unassigned_items = epic_throughput['UNASSIGNED']

        self.results_report += unassigned.format(throughput=unassigned_items)
