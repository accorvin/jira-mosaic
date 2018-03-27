import logging


class BaseQuery(object):
    def __init__(self, query_name, client, vars):
        self.query_name = query_name
        self.client = client
        self.vars = vars
        self.result = None

    def build_query(self):
        self.queries = {}
        if not self.query_bases or len(self.query_bases) == 0:
            raise Exception('Subclass must set query base')
        for query, query_string in self.query_bases.items():
            self.queries[query] = query_string.format(**self.vars)

    def set_defaults(self):
        pass

    def run(self):
        self.results = {}
        for query, query_string in self.queries.items():
            logging.debug('Executing query: {0}'.format(query_string))
            self.results[query] = self.client.search_issues(query_string,
                                                            expand='changelog',
                                                            maxResults=False)

    def print_results(self):
        print(self.results_report)
