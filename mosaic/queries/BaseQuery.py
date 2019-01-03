import datetime


class BaseQuery(object):
    supports_rolling = False
    supports_isolated_rolling = False

    def __init__(self, query_name, client, vars, log):
        self.log = log
        self.query_name = query_name
        self.client = client
        self.vars = vars
        self.result = None
        self.rolling = vars['rolling']
        self.query_append = vars.get('query_append', '')
        if self.rolling:
            if not self.supports_rolling:
                msg = ('The specified query: "{query}" does not support the '
                       'rolling argument.').format(query=self.query_name)
                raise Exception(msg)
            if not self.supports_isolated_rolling:
                today = datetime.date.today()
                begin = datetime.datetime.strptime(vars['begin_date'],
                                                   '%Y-%m-%d')
                end = datetime.datetime.strptime(vars['end_date'],
                                                 '%Y-%m-%d')
                if not (today >= begin.date() and today <= end.date()):
                    msg = ('The rolling argument can only be used for '
                           'date ranges that include today.')
                    raise Exception(msg)

    def build_query(self):
        self.queries = {}
        if not self.query_bases or len(self.query_bases) == 0:
            raise Exception('Subclass must set query base')
        for query, query_string in self.query_bases.items():
            self.queries[query] = query_string.format(**self.vars) + \
                    ' ' + self.query_append

    def set_defaults(self):
        pass

    def run(self):
        self.results = {}
        for query, query_string in self.queries.items():
            self.log.debug('Executing query: {0}'.format(query_string))
            self.results[query] = self.client.search_issues(query_string,
                                                            expand='changelog',
                                                            maxResults=False)

    def print_results(self):
        for result in self.results_report:
            print(self.template.format(**result))
