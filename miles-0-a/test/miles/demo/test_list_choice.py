from src.miles.shared.collector import PluginCollector
from src.miles.shared.matching_core import MatchingCore
from src.miles.shared.matching_core_factory import create_matching_core
from src.miles.shared.register import MilesRegister
from test.miles.demo.test_errors import MockCommandExecutor


class SimplePluginCollector(PluginCollector):

    def collect_plugins(self):
        register = MilesRegister()
        plugin_register = register.create_plugin_register("letters")
        namespace_init = plugin_register.add_namespace("letters", "h")

        namespace_init.add_command("list_choice", "V [(A, B, C, D, E)]", MockCommandExecutor())


def test_choice():
    SimplePluginCollector().collect_plugins()
    matching_core: MatchingCore = create_matching_core()

    structure = matching_core.recognize("v a b c d e", namespace="letters")
    list_item = structure.get_root().children()[1]
    assert len(list_item.children()) == 5
