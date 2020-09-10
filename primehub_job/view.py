import datetime
import re
import time
import traceback
from abc import ABCMeta, abstractmethod

# keep job-id and status relation in the memory
import dateutil
from ipywidgets import HTML, HBox, VBox

__status_views = dict()


class JobStatusViewer(metaclass=ABCMeta):

    def __init__(self, job_id):
        self.job_id = job_id

    @abstractmethod
    def show(self, job_status):
        pass


class DefaultJobStatusViewer(JobStatusViewer):

    def show(self, job_status):
        print("The job is {}. (Reason: {}, Message: {})".format(
            job_status['phase'], job_status['reason'], job_status['message']))


def duration(startTime, finishTime):
    if startTime is None:
        return "-"

    if finishTime is None:
        finishTime = datetime.datetime.now()
    else:
        finishTime = dateutil.parser.parse(finishTime).replace(tzinfo=None)

    delta = finishTime - dateutil.parser.parse(startTime).replace(tzinfo=None)
    diff = datetime.timedelta(seconds=delta.total_seconds())
    output = str(diff)

    [_, hour, minute, second] = re.findall(r'(.* days, )?(\d+):(\d+):(\d+)', output)[0]

    # convert "3 days, 0:12:34" format to "72:12:34"
    if diff.days > 0:
        hour = int(hour) + diff.days * 24

    return "{:02d}:{:02d}:{:02d}".format(int(hour), int(minute), int(second))


class IPyWidgetsViewer(JobStatusViewer):

    def __init__(self, job_id):
        super().__init__(job_id)
        self.status = HTML(value=self.create_job_widget_html('Status', '-'))
        self.duration = HTML(value=self.create_job_widget_html('Duration', '-'))
        self.reason = HTML(value=self.create_job_widget_html('Reason', '-'))
        self.extra = HTML(value="")
        self.message = HTML(value="")
        self.build_widgets()

    def create_job_widget_html(self, title, content):
        return """<div style="background-color: #f0f0f0; padding: 10px;">
            <div style="font-size: 8pt; color: rgb(120,120,120);">{}</div>
            <b style="font-size: 16pt;">{}</b>
        </div>""".format(title, content)

    def build_widgets(self):
        from IPython.core.display import display
        display(VBox([HBox([self.status, self.duration, self.reason]), self.extra, self.message]))

    def show_reminder(self, job_status):
        if 'wait_and_get_phjob_result' in [x.name for x in traceback.extract_stack()]:
            self.extra.value = ""
            return

        if job_status['finishTime'] is not None:
            self.extra.value = ""
        else:
            self.extra.value = "<i>The job is not completed. Please wait and get the result next time.</i>"

    def show(self, job_status):

        phase = job_status['phase']
        self.status.value = self.create_job_widget_html('Status', phase)

        if phase == 'Pending' or phase == 'Preparing':
            self.message.value = ""
            self.reason.value = self.create_job_widget_html('Reason', "-")
            self.duration.value = self.create_job_widget_html('Duration', "-")
            self.show_reminder(job_status)
            return

        self.duration.value = self.create_job_widget_html('Duration',
                                                          duration(job_status['startTime'], job_status['finishTime']))

        if not job_status['message']:
            self.message.value = ""
        else:
            self.message.value = """<div><b>Message: </b>%s</div>""" % job_status['message']

        self.reason.value = self.create_job_widget_html('Reason', job_status['reason'])
        self.show_reminder(job_status)


__default_viewer_class = IPyWidgetsViewer


def set_default_viewer_class(cls):
    global __default_viewer_class
    __default_viewer_class = cls


def get_view_by_id(job_id) -> JobStatusViewer:
    if job_id not in __status_views:
        __status_views[job_id] = __default_viewer_class(job_id)

    return __status_views[job_id]
