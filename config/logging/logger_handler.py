import logging
import os
import pathlib
import re
import time
from datetime import datetime, timedelta
from logging.handlers import TimedRotatingFileHandler

import requests


class TimedRotatingFileHandlerWithZip(TimedRotatingFileHandler):
    """
    Override TimedRotatingFileHandler for move old logs to path - /old/.

    In doRollover -do a rollover; in this case, a date/time stamp is appended to the filename
    when the rollover happens. And also checks and executes backupCount and oldbackupCount.

    backupCount - the number of logs in quick access.
    oldbackupCount - the number of logs to be stored in the old folder.
    If they are greater than this value, the old ones are deleted.
    """

    def __init__(self, filename, when, interval, backupCount, oldbackupCount):
        self.oldbackupCount = int(oldbackupCount)
        self.base_name = pathlib.Path(filename)
        self.logs_dir_name = self.base_name.parent
        self.old_logs_dir_name = self.logs_dir_name.joinpath("old")

        pathlib.Path(self.old_logs_dir_name).mkdir(parents=True, exist_ok=True)

        super().__init__(
            filename=str(filename),
            when=str(when),
            interval=int(interval),
            backupCount=int(backupCount),
        )
        self.file_path = pathlib.Path(self.baseFilename)

    def getFilesToMoving(self):
        result = []

        regex = f"^(debug|error)_{self.extMatch.pattern[1:-1]}.log$"
        compile_pattern = re.compile(regex, re.ASCII)

        for filename in self.logs_dir_name.iterdir():
            # Our files could be just about anything after custom naming, but
            # likely candidates are of the form
            # foo.log.DATETIME_SUFFIX or foo.DATETIME_SUFFIX.log
            if not compile_pattern.match(filename.name):
                continue
            result.append(pathlib.PurePath.joinpath(self.logs_dir_name, filename))
        if len(result) < self.backupCount:
            result = []
            return result
        result = sorted(result[: len(result) - self.backupCount])
        return result

    def getFilesToDelete(self):
        old_logs = [log for log in self.old_logs_dir_name.iterdir()]
        if len(old_logs) > self.oldbackupCount:
            logs_to_delete = sorted(old_logs)[: len(old_logs) - self.oldbackupCount]
            for old_log in logs_to_delete:
                os.remove(old_log)

    def doRollover(self):  # Noqa
        if self.stream:
            self.stream.close()
            self.stream = None

        currentTime = int(time.time())  # Get the time that this sequence started at and make it a TimeTuple.
        dstNow = time.localtime(currentTime)[-1]
        time_point = self.rolloverAt - self.interval
        timeTuple = time.localtime(time_point)
        dstThen = timeTuple[-1]
        if dstNow != dstThen:
            if dstNow:
                addend = 3600
            else:
                addend = -3600
            timeTuple = time.localtime(time_point + addend)

        rotated_filename = f"{self.base_name.stem}_{time.strftime(self.suffix, timeTuple)}{self.base_name.suffix}"

        rotated_filepath = self.rotation_filename(self.logs_dir_name.joinpath(rotated_filename))
        if rotated_filepath.exists():
            os.remove(rotated_filepath)
        self.rotate(self.baseFilename, rotated_filepath)

        for file_path in self.getFilesToMoving():
            # Moving old log files to the old's path.
            new_file_path = self.old_logs_dir_name.joinpath(file_path.name)
            os.replace(file_path, new_file_path)

        self.getFilesToDelete()  # Delete the oldest log files in the old's path.

        if not self.delay:
            self.stream = self._open()
        newRolloverAt = self.computeRollover(currentTime)
        while newRolloverAt <= currentTime:
            newRolloverAt = newRolloverAt + self.interval

        # If DST changes and midnight or weekly rollover, adjust for this.
        if self.when == "MIDNIGHT" or self.when.startswith("W"):
            dstAtRollover = time.localtime(newRolloverAt)[-1]
            if dstNow != dstAtRollover:
                if not dstNow:
                    addend = -3600  # DST kicks in before next rollover, so we need to deduct an hour
                else:
                    addend = 3600  # DST bows out before next rollover, so we need to add an hour
                newRolloverAt += addend
        self.rolloverAt = newRolloverAt


class RemoteLogger:
    def __init__(self, email, password, login_url, refresh_url, log_url):
        self.email = email
        self.password = password
        self.login_url = login_url
        self.refresh_url = refresh_url
        self.log_url = log_url
        self.access_token = None
        self.refresh_token = None
        self.token_expiry = None
        self._authenticate()

    def _authenticate(self):
        response = requests.post(self.login_url, json={"email": self.email, "password": self.password})
        if response.status_code == 200:
            data = response.json()
            self.access_token = data["access_token"]
            self.refresh_token = data["refresh_token"]
            self.token_expiry = datetime.now() + timedelta(days=7)
        else:
            raise Exception(f"Authentication failed: {response.status_code} {response.text}")

    def _refresh_token(self):
        response = requests.post(self.refresh_url, json=self.refresh_token)
        if response.status_code == 200:
            data = response.json()
            self.access_token = data["access_token"]
            self.refresh_token = data["refresh_token"]
            self.token_expiry = datetime.now() + timedelta(days=7)
        else:
            raise Exception(f"Token refresh failed: {response.status_code} {response.text}")

    def _check_token_validity(self):
        if datetime.now() >= self.token_expiry:
            self._refresh_token()

    def log(self, log_level, message, extra_info=None):
        self._check_token_validity()
        headers = {
            "Authorization": f"{self.access_token}",
            "Content-Type": "application/json",
            "accept": "application/json",
        }
        log_data = {"log_level": log_level, "message": message, "extra_info": extra_info or ""}
        response = requests.post(self.log_url, headers=headers, json=log_data)
        if response.status_code != 200:
            raise Exception(f"Log sending failed: {response.status_code} {response.text}")


class RemoteLoggerHandler(logging.Handler):
    def __init__(self, email, password, login_url, refresh_url, log_url):
        super().__init__()
        self.remote_logger = RemoteLogger(email, password, login_url, refresh_url, log_url)

    def emit(self, record):
        log_entry = self.format(record)
        self.remote_logger.log(record.levelname, log_entry)
