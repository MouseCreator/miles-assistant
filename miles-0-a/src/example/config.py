from src.miles.shared.context.text_recognize_context import TextRecognizeContext
from src.miles.shared.context_analyzer import TypedContextAnalyzer
from src.miles.shared.executor.command_executor import CommandExecutor
from src.miles.shared.executor.command_structure import CommandStructure, CommandNode
from src.miles.shared.executor.executor_utils import CommandStructureSearch
from src.miles.shared.matching_core import MatchingCore
from src.miles.shared.matching_core_factory import create_matching_core
from src.miles.shared.register import MilesRegister


class NameContextAnalyzer(TypedContextAnalyzer):
    """
    Розпізнавач імен. Розпізнає поточний токен лише якщо це слово, що починається на літеру 'M'
    """
    def invoke(self, context: TextRecognizeContext):
        current_string:str = context.current()
        if current_string.startswith('M'):
            context.consume(certainty=100) # розпізнає поточний токен з впевненістю 100
        else:
            context.fail() # повертається помилка

class DemoContext:
    """
    Клас, що збирає привітання. Використовується виконавцем команди
    """
    def __init__(self):
        self.messages = []
    def write(self, message: str):
        self.messages.append(message) # запам'ятовує повідомлення

class HelloCommandExecutor(CommandExecutor):
    """
    Виконавець команди привітання
    Записує повідомлення про те, що когось привітали, у DemoContext
    """
    def on_recognize(self, command_structure: CommandStructure, demo_context: DemoContext):
        root: CommandNode = command_structure.get_root()
        search = CommandStructureSearch(root)
        name: str = search.find_one_matching("name").any()
        demo_context.write(f'You greeted {name}')

if __name__ == '__main__':
    register = MilesRegister()
    plugin_register = register.create_plugin_register("hello") # створюється плагін hello
    namespace_init = plugin_register.add_namespace("hello", "h") # створюється простір імен hello

    namespace_init.add_command("c1", "(HI, HELLO, HEY) name", HelloCommandExecutor()) # створюється команда
    namespace_init.add_matching("name", NameContextAnalyzer()) # відповідність name зв'язується з розпізнавачем

    matching_core: MatchingCore = create_matching_core() # збірка ядра розпізнавання

    demo_context = DemoContext()

    # розпізнавання та виконання команд
    matching_core.recognize_and_execute("hi Michael", namespace="hello", context=demo_context)
    matching_core.recognize_and_execute("hello Maria", namespace="hello", context=demo_context)
    matching_core.recognize_and_execute("hey Mario", namespace="hello", context=demo_context)

    # вивід результатів
    messages = demo_context.messages
    for message in messages:
        print(message)
    print(f'Total greetings: {len(messages)}')

"""
Вивід роботи програми:

You greeted Michael
You greeted Maria
You greeted Mario
Total greetings: 3
"""