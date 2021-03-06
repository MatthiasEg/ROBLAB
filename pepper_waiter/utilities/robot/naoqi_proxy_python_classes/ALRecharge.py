#!/usr/bin/env python
# Class autogenerated from .\alrechargeproxy.h
# by Sammy Pfeiffer's <Sammy.Pfeiffer at student.uts.edu.au> generator
# You need an ALBroker running





class ALRecharge(object):
    def __init__(self, session):
        self.session = session
        self.proxy = None

    def force_connect(self):
        self.proxy = self.session.service("ALRecharge")

    def adjustDockingPosition(self, arg1):
        """.

        :param std::vector<std::vector<float> > arg1: arg
        :returns int: 
        """
        if not self.proxy:
            self.proxy = self.session.service("ALRecharge")
        return self.proxy.adjustDockingPosition(arg1)

    def dockOnStation(self):
        """.

        :returns int: 
        """
        if not self.proxy:
            self.proxy = self.session.service("ALRecharge")
        return self.proxy.dockOnStation()

    def getMaxNumberOfTries(self):
        """.

        :returns int: 
        """
        if not self.proxy:
            self.proxy = self.session.service("ALRecharge")
        return self.proxy.getMaxNumberOfTries()

    def getStationPosition(self):
        """.

        :returns std::vector<float>: 
        """
        if not self.proxy:
            self.proxy = self.session.service("ALRecharge")
        return self.proxy.getStationPosition()

    def getStatus(self):
        """.

        :returns int: 
        """
        if not self.proxy:
            self.proxy = self.session.service("ALRecharge")
        return self.proxy.getStatus()

    def getUseTrackerSearcher(self):
        """.

        :returns bool: 
        """
        if not self.proxy:
            self.proxy = self.session.service("ALRecharge")
        return self.proxy.getUseTrackerSearcher()

    def goToStation(self):
        """.
        """
        if not self.proxy:
            self.proxy = self.session.service("ALRecharge")
        return self.proxy.goToStation()

    def leaveStation(self):
        """.

        :returns int: 
        """
        if not self.proxy:
            self.proxy = self.session.service("ALRecharge")
        return self.proxy.leaveStation()

    def lookForStation(self):
        """.

        :returns AL::ALValue: 
        """
        if not self.proxy:
            self.proxy = self.session.service("ALRecharge")
        return self.proxy.lookForStation()

    def moveInFrontOfStation(self):
        """.

        :returns int: 
        """
        if not self.proxy:
            self.proxy = self.session.service("ALRecharge")
        return self.proxy.moveInFrontOfStation()

    def ping(self):
        """Just a ping. Always returns true

        :returns bool: returns true
        """
        if not self.proxy:
            self.proxy = self.session.service("ALRecharge")
        return self.proxy.ping()

    def setMaxNumberOfTries(self, arg1):
        """.

        :param int arg1: arg
        """
        if not self.proxy:
            self.proxy = self.session.service("ALRecharge")
        return self.proxy.setMaxNumberOfTries(arg1)

    def setUseTrackerSearcher(self, arg1):
        """.

        :param bool arg1: arg
        """
        if not self.proxy:
            self.proxy = self.session.service("ALRecharge")
        return self.proxy.setUseTrackerSearcher(arg1)

    def stopAll(self):
        """.
        """
        if not self.proxy:
            self.proxy = self.session.service("ALRecharge")
        return self.proxy.stopAll()

    def subscribe(self):
        """.
        """
        if not self.proxy:
            self.proxy = self.session.service("ALRecharge")
        return self.proxy.subscribe()

    def unsubscribe(self):
        """.
        """
        if not self.proxy:
            self.proxy = self.session.service("ALRecharge")
        return self.proxy.unsubscribe()

    def version(self):
        """Returns the version of the module.

        :returns str: A string containing the version of the module.
        """
        if not self.proxy:
            self.proxy = self.session.service("ALRecharge")
        return self.proxy.version()
