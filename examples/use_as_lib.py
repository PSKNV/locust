import gevent
from locust import HttpLocust, TaskSet, task, between
from locust.runners import LocalLocustRunner
from locust.env import Environment
from locust.stats import stats_printer
from locust.log import setup_logging
from locust.web import WebUI

setup_logging("INFO", None)


class User(HttpLocust):
    wait_time = between(1, 3)
    host = "https://docs.locust.io"

    @task
    def my_task(self):
        self.client.get("/")

    @task
    def task_404(self):
        self.client.get("/non-existing-path")

# setup Environment and Runner
env = Environment(locust_classes=[User])
runner = env.create_local_runner()

# start a WebUI instance
web_ui = env.create_web_ui("127.0.0.1", 8089)

# start a greenlet that periodically outputs the current stats
gevent.spawn(stats_printer(env.stats))

# start the test
runner.start(1, hatch_rate=10)

# in 60 seconds stop the runner
gevent.spawn_later(10, lambda: runner.quit())

# wait for the greenlets
runner.greenlet.join()

# stop the web server for good measures
web_ui.stop()