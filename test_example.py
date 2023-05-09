from __future__ import annotations

from decorators import Providers

from random import randint

from provider import Provider


class Dependency(str):
    def __init__(self, random_: int):
        self.random_ = random_


def dependency_factory() -> Dependency:
    return Dependency(randint(1, 100))


dependency_provider = Provider(class_=Dependency, factory=dependency_factory)


@Providers.module(
    providers=[
        dependency_provider,
    ]
)
class RootModule:
    def __init__(self, dependency: dependency_provider):
        print(dependency.random_)


module = RootModule.resolve()