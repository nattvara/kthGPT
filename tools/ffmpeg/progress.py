from threading import Thread, Event
import tempfile
import time


class ProgressFFmpeg(Thread):
    def __init__(self, total_duration_seconds, progress_update_callback):
        Thread.__init__(self, name='ProgressFFmpeg')
        self.stop_event = Event()
        self.output_file = tempfile.NamedTemporaryFile(mode='w+', delete=False)
        self.total_duration_seconds = total_duration_seconds
        self.progress_update_callback = progress_update_callback

    def run(self):
        while not self.stop_event.is_set():
            latest_progress = self.get_latest_ms_progress()
            if latest_progress is not None:
                completed_percent = latest_progress / self.total_duration_seconds
                self.progress_update_callback(completed_percent)
            time.sleep(.01)

    def get_latest_ms_progress(self):
        lines = self.output_file.readlines()
        if lines:
            for line in lines:
                if 'out_time_ms' in line:
                    out_time_ms = line.split('=')[1]
                    return int(out_time_ms) / 1000000
        return None

    def stop(self):
        self.stop_event.set()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args, **kwargs):
        self.stop()
