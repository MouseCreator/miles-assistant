from abc import ABC, abstractmethod


class PluginCollector(ABC):
    @abstractmethod
    def collect_plugins(self):
        pass