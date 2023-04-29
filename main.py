from __future__ import annotations

from decorators import Providers


@Providers.injectable()
class SomeDep:
    a = 12


@Providers.injectable()
class TestDep:
    a = 12


@Providers.injectable()
class TestProvider:
    def __init__(self, dep: TestDep, someDep: SomeDep):
        self._dep = dep


@Providers.module(
    providers=[TestDep],
    exports=[TestDep],
)
class NestedModule: ...


@Providers.module(
    providers=[SomeDep],
    exports=[SomeDep]
)
class RootModule: ...


@Providers.module(
    imports=[
        NestedModule,
        RootModule,
    ],
    providers=[TestProvider]
)
class SecondModule:
    def __init__(self, dep: TestProvider):
        self._dep = dep

    def start(self):
        print(f'App started {self._dep._dep.a}')



module = RootModule
module.resolve()

module2 = SecondModule
module2.resolve()

# main_ = module()
# main_.start()


a = 12