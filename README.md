# Pid - Python injectable dependencies

## Description:
You can use pid for construct tree based architecture with simple mechanism of sharing dependencies.
Pid allows to share modules wia export | import attributes. Reassign providers for specific modules | providers.
etc...

## Simple example:

```python
from pid import Pid, BootStrap

@Pid.injectable()
class Depedency:
    def do_something(self):
        print('Something_done')


@Pid.module(providers=[Depedency])
class RootModule:
    def __init__(self, dependency: Depedency):
        self._dependency = dependency

    def start(self):
        self._dependency.do_something()
        
root = BootStrap.resolve(RootModule)

root.start()  # Something_done
```
