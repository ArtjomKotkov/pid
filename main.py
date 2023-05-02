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
        dep: TestDep,
        resolved_some_dep: SomeDep,
        unresolved_some_dep: Provider[SomeDep]
    ):
        resolved_tag = unresolved_some_dep.resolve('someTag')
        resolved_untag = resolved_some_dep

        resolved_tag.a = 14
        resolved_untag.a = 20

        print(resolved_tag.a, resolved_untag.a)


@Providers.module(
    providers=[SomeDep],
    exports=[SomeDep],
)
class SecondModule: ...


@Providers.module(
    providers=[TestDep],
    exports=[TestDep]
)
class OneModule: ...


@Providers.module(
    imports=[
        OneModule,
        SecondModule,
    ],
    providers=[TestProvider],
)
class RootModule:
    def __init__(
        self,
        dep: TestProvider,
        resolved_some_dep: SomeDep,
        unresolved_some_dep: Provider[SomeDep]
    ):
        self._dep = dep

        resolved_tag = unresolved_some_dep.resolve('someTag')
        resolved_untag = resolved_some_dep

        resolved_tag2 = unresolved_some_dep.resolve('someTag2')

        print(resolved_tag.a, resolved_untag.a, resolved_tag2.a)

    def start(self):
        print(f'App started {self._dep._dep.a}')


module2 = RootModule
module2.resolve()

# main_ = module()
# main_.start()


a = 12