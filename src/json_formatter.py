# Python imports
import json
from typing import Dict, Any

# Project imports
from common import Formatter


class JSONFormatter(Formatter):
    """
    Generates a JSON output given a results dictionary
    """
    def write_report(self, data: Dict[str, Any], output_file: str):
        with open(output_file, 'w') as f:
            f.write(json.dumps(data))
