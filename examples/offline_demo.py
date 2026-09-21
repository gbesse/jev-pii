# Purpose: Demonstrate fully local deterministic detection.
from jev_pii import scan_columns
print(scan_columns({'contact':['demo@example.test'],'note':['synthetic note']},local_only=True))
