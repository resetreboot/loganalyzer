# Python imports
import argparse
import sys
from typing import Tuple, List, Dict, Any

# Project imports
from common import LogTypeInfo, Formatter, Operation
from json_formatter import JSONFormatter
from operations import MostFrequentIps, LessFrequentIps, Events, TotalBytes


class LogAnalyzer:
    """
    Main business logic of the parsing tool
    """
    DEFAULT_SEPARATOR = ''
    DEFAULT_FIELDS = [('timestamp', LogTypeInfo.timestamp),
                      ('header_size', LogTypeInfo.integer),
                      ('ip', LogTypeInfo.string),
                      ('resp_code', LogTypeInfo.string),
                      ('resp_size', LogTypeInfo.integer),
                      ('method', LogTypeInfo.string),
                      ('url', LogTypeInfo.string),
                      ('username', LogTypeInfo.string),
                      ('access_destination', LogTypeInfo.string),
                      ('resp_type', LogTypeInfo.string)]

    def __init__(self, logs: List[str], output: str):
        self.logs = logs
        self.output_file = output
        self.ignore_empty_fields = True
        self.separator = LogAnalyzer.DEFAULT_SEPARATOR
        self.log_fields = LogAnalyzer.DEFAULT_FIELDS
        self.formatter = JSONFormatter()

        self.operations = []

    def define_input_format(self, fields: List[Tuple[str, LogTypeInfo]],
                            separator: str = '', ignore_empty_fields: bool = True):
        """
        Allows definition of a new format of the fields extracted from the log
        """
        self.separator = separator
        self.log_fields = fields
        self.ignore_empty_fields = ignore_empty_fields

    def add_operation(self, operation: Operation):
        """
        Include a new operation in the chain
        """
        self.operations.append(operation)

    def change_output_formatter(self, formatter: Formatter):
        """
        Change the default formatter to a self defined one
        """
        self.formatter = formatter

    def _parse_field(self, field: str, field_type: LogTypeInfo) -> Any:
        """
        Given a field an a type, parses it and returns the expected value
        """
        try:
            if field_type == LogTypeInfo.integer:
                return int(field)

            if field_type == LogTypeInfo.timestamp:
                return float(field)

        except:
            # If the conversion errs, we'd rather return the value unchanged
            pass

        # String type field: LogTypeInfo.string
        return field

    def _read_line(self, line: str) -> Dict[str, Any]:
        """
        Parses the line and assigns the labels to a dictionary based
        on the format for this object
        """
        separator = self.separator or ' '
        field_counter = 0
        result = {}
        for elem in line.split(separator):
            if len(elem) == 0 and self.ignore_empty_fields:
                # Empty fields due to extra separators are ignored
                continue

            if elem == '\n':
                break

            if field_counter >= len(self.log_fields):
                break

            label, field_type = self.log_fields[field_counter]
            result[label] = self._parse_field(elem, field_type)
            field_counter += 1

        return result

    def process(self):
        """
        Start reading the logs, process them and generate the report
        """
        output_data = {}
        print(self.logs)

        for file in self.logs:
            with open(file, 'r') as f:
                for line in f:
                    if len(line) > 0:
                        processed = self._read_line(line)
                        if len(processed.keys()) > 0:
                            for op in self.operations:
                                op.process(processed)

        # Get the data gathered from our operations
        for op in self.operations:
            output_data = op.generate_output(output_data)

        # Write the output
        self.formatter.write_report(output_data, self.output_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Log analyzing tool')

    parser.add_argument('--mostfreqip', '-mfp', action="store_true", default=False, help='Most frequent IP')
    parser.add_argument('--lessfreqip', '-lfp', action="store_true", default=False, help='Less frequent IP')
    parser.add_argument('--events', '-e', action="store_true", default=False, help='Events per second')
    parser.add_argument('--totalbytes', '-b', action="store_true", default=False, help='Total amount of bytes exchanged')

    # Output files to produce
    parser.add_argument('--output', '-o', nargs=1, help='Output file in JSON format')

    # Input files to consume
    parser.add_argument('--logs', '-l', nargs=1, help='Logs to analyze, comma separated')

    args = parser.parse_args()

    if len(args.logs) == 0:
        parser.print_help()
        sys.exit(1)

    log_files = [elem.strip() for elem in args.logs[0].split(",")]

    analyzer = LogAnalyzer(log_files, args.output[0])

    if args.mostfreqip:
        # Analize the most frequent IPs
        mfp = MostFrequentIps()
        analyzer.add_operation(mfp)

    if args.lessfreqip:
        # Analize the less frequent IPs
        lfp = LessFrequentIps()
        analyzer.add_operation(lfp)

    if args.events:
        # Get the events per second
        events = Events()
        analyzer.add_operation(events)

    if args.totalbytes:
        # Get the total amount of bytes exchanged
        totalbytes = TotalBytes()
        analyzer.add_operation(totalbytes)

    # Process the logs
    analyzer.process()
