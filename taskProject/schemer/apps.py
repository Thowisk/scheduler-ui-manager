import traceback

from django.apps import AppConfig


class SchemerConfig(AppConfig):
    name = 'schemer'

    def ready(self):
        from . import schedulerclient
        try:
            schedulerclient.SchedulerClient().start()
        except(Exception):
            print(' /!\\ Couldn\'t get a connection to the scheduler service /!\\')
            # traceback.print_exc(Exception)