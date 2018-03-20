from .ThroughputQuery import ThroughputQuery
from .ThroughputQuery import ThroughputbyepicQuery
from .LeadtimeQuery import LeadtimeQuery
from .LeadtimeQuery import LeadtimebyepicQuery
from .CycletimeQuery import CycletimeQuery
from .StatusdurationQuery import StatusdurationQuery


query_map = {
    'throughput': ThroughputQuery,
    'throughputbyepic': ThroughputbyepicQuery,
    'leadtime': LeadtimeQuery,
    'leadtimebyepic': LeadtimebyepicQuery,
    'cycletime': CycletimeQuery,
    'statusduration': StatusdurationQuery
}
