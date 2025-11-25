import os

from redis import Redis
from rq import Queue

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_conn = None
transcription_queue = None

try:
	redis_conn = Redis.from_url(REDIS_URL)
	# verify connection
	redis_conn.ping()
	transcription_queue = Queue("transcriptions", connection=redis_conn, default_timeout=60 * 30)
except Exception:
	# Fallback to a lightweight in-memory stub queue so tests and dev can run
	# without redis. The stub supports enqueue(job_fn, **kwargs) and simply
	# executes the function synchronously.
	class _StubQueue:
		def enqueue(self, fn, **kwargs):
			# execute synchronously for local dev/testing
			try:
				fn(**kwargs)
			except TypeError:
				# some job entrypoints expect positional args
				fn(*kwargs.values())

	transcription_queue = _StubQueue()

