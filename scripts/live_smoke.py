# Purpose: Guard the unwired paid semantic adapter.
import os
if not os.getenv('TYPESAFE_API_KEY'):raise SystemExit('Set TYPESAFE_API_KEY')
raise SystemExit('Live semantic transport is not wired in this alpha; zero requests made')
