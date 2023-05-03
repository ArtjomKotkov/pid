from __future__ import annotations

from decorators import Providers
from provider import Provider


@Providers.injectable()
class SomeDep:
    a = 12


@Providers.injectable()
class TestDep:
    a = 12


@Providers.injectable()
class TestProvider:
    def __init__(
        self,
        # dep: TestDep,
        resolved_some_dep: SomeDep,
        unresolved_some_dep: Provider[SomeDep],
    ):
        ...


@Providers.module(
    providers=[SomeDep],
    exports=[SomeDep],
)
class SecondModule:
    def __init__(self, some: SomeDep):
        ...


@Providers.module(
    providers=[TestDep],
    exports=[TestDep]
)
class OneModule: ...


@Providers.module(
    imports=[
        # OneModule,
        SecondModule,
    ],
    providers=[
        TestProvider,
        SomeDep
    ],
)
class RootModule:
    def __init__(
        self,
        resolved_dep: SomeDep,
        unresolved_some_dep: Provider[SomeDep],
    ):
        self._unresolved_some_dep = unresolved_some_dep
        self._resolved_dep = resolved_dep

    def test(self):
        test = self._unresolved_some_dep.resolve('tag')

module = RootModule.resolve()
module.test()

a = 12