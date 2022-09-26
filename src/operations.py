# Python imports
from typing import Dict, Any
from collections import Counter

# Project imports
from common import Operation


class MostFrequentIps(Operation):
    """
    Gets the most frequent IP from a log
    """
    def __init__(self):
        """
        We create a counter to keep the data in this class
        """
        self.counter = Counter()

    def process(self, processed: Dict[str, Any]):
        self.counter[processed['ip']] += 1

    def generate_output(self, output_data: Dict[str, Any]) -> Dict[str, Any]:
        mfp = self.counter.most_common(1)[0]
        # We kind of want to avoid affecting the passed on dictionary as we
        # return it later
        output = dict(output_data)
        output["mostfrequentip"] = {mfp[0]: mfp[1]}

        return output


class LessFrequentIps(MostFrequentIps):
    """
    Gets the least frequent IP from the log
    """
    def generate_output(self, output_data: Dict[str, Any]) -> Dict[str, Any]:
        fp = self.counter.most_common()
        fp.reverse()

        lfp = fp[0]

        output = dict(output_data)
        output["lessfrequentip"] = {lfp[0]: lfp[1]}

        return output


class Events(Operation):
    """
    Generates an average of events per second, needs timestamp in Epoch format
    """
    def __init__(self):
        self.initial_second = 0
        self.last_second = 0
        self.total_events = 0

    def process(self, processed: Dict[str, Any]):
        """
        Here we make sure that we get the first timestamp stored and the last
        then the total of events logged and divide to get an average of events
        per second
        """
        epoch = int(processed['timestamp'])
        # Since we can't guarantee the logs come in the correct order, we check
        # with each line
        if epoch < self.initial_second:
            self.initial_second = epoch

        # Same with ending second
        if epoch > self.last_second:
            self.last_second = epoch

        self.total_events += 1

    def generate_output(self, output_data: Dict[str, Any]) -> Dict[str, Any]:
        total_seconds = self.last_second - self.initial_second
        events_per_second = self.total_events / total_seconds

        output = dict(output_data)
        output["events_per_second"] = events_per_second

        return output


class TotalBytes(Operation):
    """
    Generates a total of bytes exchanged
    """
    def __init__(self):
        self.total = 0
        self.headers = 0
        self.bodies = 0

    def process(self, processed: Dict[str, Any]):
        self.total += processed["header_size"] + processed["resp_size"]
        self.headers += processed["header_size"]
        self.bodies += processed["resp_size"]

    def generate_output(self, output_data: Dict[str, Any]) -> Dict[str, Any]:
        output = dict(output_data)

        output["total_bytes"] = self.total
        output["headers_bytes"] = self.headers
        output["body_bytes"] = self.bodies

        return output
