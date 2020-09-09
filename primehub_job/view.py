# keep job-id and status relation in the memory
__status_views = dict()

from abc import ABCMeta, abstractmethod


class JobStatusViewer(metaclass=ABCMeta):

    def __init__(self):
        pass

    @abstractmethod
    def show(self, job_status):
        pass


class DefaultJobStatusViewer(JobStatusViewer):

    def show(self, job_status):
        print("The job is {}. (Reason: {}, Message: {})".format(
            job_status['phase'], job_status['reason'], job_status['message']))


__default_viewer_class = DefaultJobStatusViewer


def set_default_viewer_class(cls):
    global __default_viewer_class
    __default_viewer_class = cls


def get_view_by_id(job_id) -> JobStatusViewer:
    if job_id not in __status_views:
        __status_views[job_id] = __default_viewer_class()

    return __status_views[job_id]
