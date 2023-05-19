from typing import Dict, Any, List, Optional
import subprocess
import os



ALL_SERVICES = [
    "orgdata",
    "taskman",
    "query",
]



def _start_process(directory: str) -> Any:
    return subprocess.Popen(
        ["run_service.sh"],
        cwd=os.path.join("..", directory)
    )



def run_services() -> List[Any]:
    return [
        _start_process(service_directory) for service_directory in ALL_SERVICES
    ]


