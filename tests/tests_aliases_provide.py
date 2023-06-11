from typing import TypeVar, Generic

import pytest

from pid import BootStrap, Pid
from pid.shared import CannotResolveDependency, MultipleProvidersForAlias


def test_alias():
    class Interface: ...

    @Pid.injectable()
    class TestProvider(Interface): ...

    @Pid.module(providers=[TestProvider])
    class TestModule:
        def __init__(self, provider: Interface):
            self.provider = provider

    test_module = BootStrap.resolve(TestModule)

    assert isinstance(test_module.provider, TestProvider)
    assert issubclass(test_module.provider.__class__, Interface)


def test_generic_alias():
    T = TypeVar('T')

    class Model: ...

    class Interface(Generic[T]): ...

    @Pid.injectable()
    class TestProvider(Interface[Model]): ...

    @Pid.module(providers=[TestProvider])
    class TestModule:
        def __init__(self, provider: Interface[Model]):
            self.provider = provider

    test_module = BootStrap.resolve(TestModule)

    assert isinstance(test_module.provider, TestProvider)
    assert issubclass(test_module.provider.__class__, Interface)


def test_accurate_alias():
    T = TypeVar('T')

    class Model: ...

    class Interface(Generic[T]): ...

    @Pid.injectable()
    class TestProvider(Interface[Model]): ...

    @Pid.module(providers=[TestProvider])
    class TestModule:
        def __init__(self, provider: Interface):
            self.provider = provider

    with pytest.raises(CannotResolveDependency):
        BootStrap.resolve(TestModule)


def test_multiple_aliases_acquired():
    T = TypeVar('T')

    class Model: ...

    class Interface(Generic[T]): ...

    @Pid.injectable()
    class TestProvider(Interface[Model]): ...

    @Pid.injectable()
    class TestProviderCopy(Interface[Model]): ...

    @Pid.module(providers=[TestProvider, TestProviderCopy])
    class TestModule:
        def __init__(self, _: TestProviderCopy, provider: Interface[Model]):
            self.provider = provider

    with pytest.raises(MultipleProvidersForAlias):
        BootStrap.resolve(TestModule)


def test_multiple_aliases_acquired_inverted():
    T = TypeVar('T')

    class Model: ...

    class Interface(Generic[T]): ...

    @Pid.injectable()
    class TestProvider(Interface[Model]): ...

    @Pid.injectable()
    class TestProviderCopy(Interface[Model]): ...

    @Pid.module(providers=[TestProviderCopy, TestProvider])
    class TestModule:
        def __init__(self, provider: Interface[Model], _: TestProviderCopy):
            self.provider = provider

    with pytest.raises(MultipleProvidersForAlias):
        BootStrap.resolve(TestModule)


def test_generic_alias_with_different_generic():
    T = TypeVar('T')

    class Model: ...

    class Model2: ...

    class Interface(Generic[T]): ...

    @Pid.injectable()
    class TestProvider(Interface[Model]): ...

    @Pid.injectable()
    class TestProvider2(Interface[Model2]): ...

    @Pid.module(providers=[TestProvider, TestProvider2])
    class TestModule:
        def __init__(self, provider: Interface[Model], provider2: Interface[Model2]):
            self.provider = provider
            self.provider2 = provider2

    test_module = BootStrap.resolve(TestModule)

    assert isinstance(test_module.provider, TestProvider)
    assert issubclass(test_module.provider.__class__, Interface)

    assert isinstance(test_module.provider2, TestProvider2)
    assert issubclass(test_module.provider2.__class__, Interface)


def test_generic_alias_with_different_generic_inverted():
    T = TypeVar('T')

    class Model: ...

    class Model2: ...

    class Interface(Generic[T]): ...

    @Pid.injectable()
    class TestProvider(Interface[Model]): ...

    @Pid.injectable()
    class TestProvider2(Interface[Model2]): ...

    @Pid.module(providers=[TestProvider2, TestProvider])
    class TestModule:
        def __init__(self, provider2: Interface[Model2], provider: Interface[Model]):
            self.provider = provider
            self.provider2 = provider2

    test_module = BootStrap.resolve(TestModule)

    assert isinstance(test_module.provider, TestProvider)
    assert issubclass(test_module.provider.__class__, Interface)

    assert isinstance(test_module.provider2, TestProvider2)
    assert issubclass(test_module.provider2.__class__, Interface)
