"""
Cronjob like scheduling abstraction in Python.
"""

from datetime import datetime, timedelta
import xbmc
import xbmcaddon

addon = xbmcaddon.Addon()
addon_id = '[%s-%s]' % (addon.getAddonInfo('id'), addon.getAddonInfo('version'))


def log(message, level=xbmc.LOGDEBUG):
    xbmc.log('%s %s' % (addon_id, message), level)


def collect_slots():

    slots = list()
    for slot in range(1, 4):
        if addon.getSetting('enabled_{}_{}'.format(slot, datetime.now().weekday())).lower() == 'false': continue
        try:
            slot_range = list()
            start = addon.getSetting('slot_{}_start_{}'.format(slot, datetime.now().weekday()))
            stop = addon.getSetting('slot_{}_stop_{}'.format(slot, datetime.now().weekday()))
            slot_range.append(timedelta(hours=int(start.split(':')[0]), minutes=int(start.split(':')[1])).seconds)
            slot_range.append(timedelta(hours=int(stop.split(':')[0]), minutes=int(stop.split(':')[1])).seconds)
            slots.append(slot_range)
        except IndexError:
            continue
    log(str(slots))
    return slots


class CronTab(object):

    """
    Simulates basic cron functionality by checking for time slots every minute.
    """

    def __init__(self):
        self.timeslots = collect_slots()
        self.timeframe = False
        self.monitor = self.SettingsMonitor()
        self.__enabled = True

    def stop(self):
        """
        Stops cron.
        """
        self.__enabled = False

    def start(self):
        """
        Starts to check every minute, if current time is member of a timeslot.
        """
        cron_time_tuple = datetime(*datetime.now().timetuple()[:5])
        while self.__enabled and not self.monitor.abortRequested():
            log('check time slots')

            if self.monitor.settings_changed:
                log('read settings')
                self.timeslots = collect_slots()
                self.monitor.settings_changed = False

            self.main_func()

            cron_time_tuple += timedelta(minutes=1)
            if datetime.now() < cron_time_tuple:
                self.monitor.waitForAbort((cron_time_tuple - datetime.now()).seconds)
        log('Cron finished')

    def main_func(self):

        now = datetime.now()
        zero = now.replace(hour=0, minute=0, second=0, microsecond=0)
        self.timeframe = False

        for slot in self.timeslots:
            if slot[0] < (now - zero).seconds < slot[1]:
                self.timeframe = True
                log('We are in a time frame, no need to handle this...')
                return

        log('We are outside of a timeframe, performing some action requested...')

    class SettingsMonitor(xbmc.Monitor):

        def __init__(self):
            xbmc.Monitor.__init__(self)
            self.settings_changed = False

        def onSettingsChanged(self):
            self.settings_changed = True
