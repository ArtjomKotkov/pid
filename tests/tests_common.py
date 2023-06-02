import pytest

from pid.shared import CannotResolveDependency, UndefinedExport, ClassIsNotInjectable
from pid import BootStrap, Pid, Provider, Tag


class TestsCombinations:

    def test_provider(self):
        @Pid.injectable()
        class TestProvider: ...

        @Pid.module(providers=[TestProvider])
        class TestModule:
            def __init__(self, provider: TestProvider):
                self.provider = provider

        test_module = BootStrap.resolve(TestModule)

        assert test_module.provider is not None

    def test_exports(self):
        __store__ = {}

        @Pid.injectable()
        class TestProvider: ...

        @Pid.module(providers=[TestProvider], exports=[TestProvider])
        class ExportModule:
            def __init__(self, provider: TestProvider):
                __store__['common_provider'] = provider

        @Pid.module(imports=[ExportModule])
        class TestModule:
            def __init__(self, provider: TestProvider):
                __store__['inherited_provider'] = provider

        BootStrap.resolve(TestModule)

        assert __store__['common_provider'] is __store__['inherited_provider']

    def test_module_exports(self):
        __store__ = {}

        @Pid.injectable()
        class TestProvider: ...

        @Pid.module(providers=[TestProvider], exports=[TestProvider])
        class ExportModuleTwo:
            def __init__(self, provider: TestProvider):
                __store__['common_provider'] = provider

        @Pid.module(imports=[ExportModuleTwo], exports=[ExportModuleTwo])
        class ExportModule: ...

        @Pid.module(imports=[ExportModule])
        class TestModule:
            def __init__(self, provider: TestProvider):
                __store__['inherited_provider'] = provider

        BootStrap.resolve(TestModule)

        assert __store__['common_provider'] is __store__['inherited_provider']

    def test_rhombus(self):
        __store__ = {}

        @Pid.injectable()
        class TestProvider: ...

        @Pid.module(providers=[TestProvider], exports=[TestProvider])
        class TopModule:
            def __init__(self, provider: TestProvider):
                __store__['common_provider'] = provider

        @Pid.module(imports=[TopModule])
        class RightModule:
            def __init__(self, provider: TestProvider):
                __store__['right_provider'] = provider

        @Pid.module(imports=[TopModule])
        class LeftModule:
            def __init__(self, provider: TestProvider):
                __store__['left_provider'] = provider

        @Pid.module(imports=[RightModule, LeftModule])
        class TestModule: ...

        BootStrap.resolve(TestModule)

        assert __store__['common_provider'] is __store__['left_provider']
        assert __store__['common_provider'] is __store__['right_provider']

    def test_use_inherit(self):
        __store__ = {}

        @Pid.injectable()
        class TestProvider: ...

        @Pid.injectable()
        class ProviderWithDep:
            def __init__(self, provider: TestProvider):
                __store__['provider_provider'] = provider

        @Pid.module(providers=[TestProvider, ProviderWithDep])
        class TestModule:
            def __init__(self, provider: TestProvider):
                __store__['module_provider'] = provider

        BootStrap.resolve(TestModule)

        assert __store__['provider_provider'] is __store__['module_provider']

    def test_use_inherit_inverted(self):
        __store__ = {}

        @Pid.injectable()
        class TestProvider: ...

        @Pid.injectable()
        class ProviderWithDep:
            def __init__(self, provider: TestProvider):
                __store__['provider_provider'] = provider

        @Pid.module(providers=[ProviderWithDep, TestProvider])
        class TestModule:
            def __init__(self, provider: TestProvider):
                __store__['module_provider'] = provider

        BootStrap.resolve(TestModule)

        assert __store__['provider_provider'] is __store__['module_provider']

    def test_reassign(self):
        __store__ = {}

        @Pid.injectable()
        class TestProvider: ...

        @Pid.injectable(providers=[TestProvider])
        class ReassignProvider:
            def __init__(self, provider: TestProvider):
                __store__['reassign_provider'] = provider

        @Pid.module(providers=[TestProvider, ReassignProvider])
        class TestModule:
            def __init__(self, provider: TestProvider):
                __store__['module_provider'] = provider

        BootStrap.resolve(TestModule)

        assert __store__['reassign_provider'] is not __store__['module_provider']

    def test_reassign_inverted(self):
        __store__ = {}

        @Pid.injectable()
        class TestProvider: ...

        @Pid.injectable(providers=[TestProvider])
        class ReassignProvider:
            def __init__(self, provider: TestProvider):
                __store__['reassign_provider'] = provider

        @Pid.module(providers=[ReassignProvider, TestProvider])
        class TestModule:
            def __init__(self, provider: TestProvider):
                __store__['module_provider'] = provider

        BootStrap.resolve(TestModule)

        assert __store__['reassign_provider'] is not __store__['module_provider']

    def test_module_reassign(self):
        __store__ = {}

        @Pid.injectable()
        class TestProvider: ...

        @Pid.module(providers=[TestProvider], exports=[TestProvider])
        class ExportModuleTwo:
            def __init__(self, provider: TestProvider):
                __store__['common_provider'] = provider

        @Pid.module(imports=[ExportModuleTwo], exports=[ExportModuleTwo])
        class ExportModule: ...

        @Pid.module(providers=[TestProvider], imports=[ExportModule])
        class TestModule:
            def __init__(self, provider: TestProvider):
                __store__['inherited_provider'] = provider

        BootStrap.resolve(TestModule)

        assert __store__['common_provider'] is not __store__['inherited_provider']

    def test_reassign_inherit(self):
        __store__ = {}

        @Pid.injectable()
        class TestProvider: ...

        @Pid.injectable()
        class InheritProvider:
            def __init__(self, provider: TestProvider):
                __store__['reassign_inherit_provider'] = provider

        @Pid.injectable(providers=[TestProvider, InheritProvider])
        class ReassignProvider: ...

        @Pid.module(providers=[ReassignProvider, TestProvider])
        class TestModule:
            def __init__(self, provider: TestProvider):
                __store__['module_provider'] = provider

        BootStrap.resolve(TestModule)

        assert __store__['reassign_inherit_provider'] is not __store__['module_provider']

    def test_reassign_inherit_inverted(self):
        __store__ = {}

        @Pid.injectable()
        class TestProvider: ...

        @Pid.injectable()
        class InheritProvider:
            def __init__(self, provider: TestProvider):
                __store__['reassign_inherit_provider'] = provider

        @Pid.injectable(providers=[InheritProvider, TestProvider])
        class ReassignProvider: ...

        @Pid.module(providers=[ReassignProvider, TestProvider])
        class TestModule:
            def __init__(self, provider: TestProvider):
                __store__['module_provider'] = provider

        BootStrap.resolve(TestModule)

        assert __store__['reassign_inherit_provider'] is not __store__['module_provider']

    def test_multiple_exports(self):
        __store__ = {}

        @Pid.injectable()
        class TestProvider: ...

        @Pid.module(providers=[TestProvider], exports=[TestProvider])
        class ExportModuleOne:
            def __init__(self, provider: TestProvider):
                __store__['export_provider_one'] = provider

        @Pid.module(providers=[TestProvider], exports=[TestProvider])
        class ExportModuleTwo:
            def __init__(self, provider: TestProvider):
                __store__['export_provider_two'] = provider

        @Pid.module(imports=[ExportModuleOne, ExportModuleTwo])
        class TestModule:
            def __init__(self, provider: TestProvider):
                __store__['inherited_provider'] = provider

        BootStrap.resolve(TestModule)

        assert __store__['inherited_provider'] is __store__['export_provider_two']
        assert __store__['inherited_provider'] is not __store__['export_provider_one']
        assert __store__['export_provider_two'] is not __store__['export_provider_one']

    def test_multiple_exports_inverted(self):
        __store__ = {}

        @Pid.injectable()
        class TestProvider: ...

        @Pid.module(providers=[TestProvider], exports=[TestProvider])
        class ExportModuleOne:
            def __init__(self, provider: TestProvider):
                __store__['export_provider_one'] = provider

        @Pid.module(providers=[TestProvider], exports=[TestProvider])
        class ExportModuleTwo:
            def __init__(self, provider: TestProvider):
                __store__['export_provider_two'] = provider

        @Pid.module(imports=[ExportModuleTwo, ExportModuleOne])
        class TestModule:
            def __init__(self, provider: TestProvider):
                __store__['inherited_provider'] = provider

        BootStrap.resolve(TestModule)

        assert __store__['inherited_provider'] is not __store__['export_provider_two']
        assert __store__['inherited_provider'] is __store__['export_provider_one']
        assert __store__['export_provider_two'] is not __store__['export_provider_one']


class TestsErrors:

    def test_not_injectable_provider(self):
        class TestProvider: ...

        @Pid.module(providers=[TestProvider])
        class TestModule: ...

        with pytest.raises(ClassIsNotInjectable):
            BootStrap.resolve(TestModule)

    def test_not_injectable_module(self):
        class SecondModule: ...

        @Pid.module(imports=[SecondModule])
        class TestModule: ...

        with pytest.raises(ClassIsNotInjectable):
            BootStrap.resolve(TestModule)

    def test_forbidden_exports(self):
        @Pid.injectable()
        class TestProvider: ...

        @Pid.module(providers=[TestProvider], exports=[])
        class ExportModule: ...

        @Pid.module(imports=[ExportModule])
        class TestModule:
            def __init__(self, _: TestProvider): ...

        with pytest.raises(CannotResolveDependency):
            BootStrap.resolve(TestModule)

    def test_export_undefined(self):
        @Pid.injectable()
        class TestProvider: ...

        @Pid.injectable()
        class UndefinedProvider: ...

        @Pid.module(providers=[TestProvider], exports=[TestProvider, UndefinedProvider])
        class ExportModule: ...

        @Pid.module(imports=[ExportModule])
        class TestModule:
            def __init__(self, _: TestProvider): ...

        with pytest.raises(UndefinedExport):
            BootStrap.resolve(TestModule)


class TestsFactory:

    def test_simple_factory(self):
        @Pid.injectable(
            factory=lambda: 'test_string'
        )
        class TestProvider(str): ...

        @Pid.module(providers=[TestProvider])
        class TestModule:
            def __init__(self, provider: TestProvider):
                self.provider = provider

        test_module = BootStrap.resolve(TestModule)

        assert isinstance(test_module.provider, str)
        assert test_module.provider == 'test_string'

    def test_factory_with_dependency_inherit(self):
        __store__ = {}

        @Pid.injectable()
        class FactoryDependency: ...

        def factory(provider: FactoryDependency):
            __store__['factory_provider'] = provider
            return TestProvider('test_string')

        @Pid.injectable(
            factory=factory
        )
        class TestProvider(str): ...

        @Pid.module(providers=[FactoryDependency, TestProvider])
        class TestModule:
            def __init__(self, provider: FactoryDependency):
                __store__['module_provider'] = provider

        BootStrap.resolve(TestModule)

        assert __store__['module_provider'] is __store__['factory_provider']

    def test_factory_with_dependency(self):
        @Pid.injectable()
        class FactoryDependency: ...

        def factory(dependency: FactoryDependency):
            assert dependency is not None
            return TestProvider('test_string')

        @Pid.injectable(
            factory=factory
        )
        class TestProvider(str): ...

        @Pid.module(providers=[FactoryDependency, TestProvider])
        class TestModule:
            def __init__(self, provider: TestProvider):
                self.provider = provider

        test_module = BootStrap.resolve(TestModule)

        assert isinstance(test_module.provider, str)
        assert test_module.provider == 'test_string'

    def test_factory_with_dependency_inverted(self):
        @Pid.injectable()
        class FactoryDependency: ...

        def factory(dependency: FactoryDependency):
            assert dependency is not None
            return TestProvider('test_string')

        @Pid.injectable(
            factory=factory
        )
        class TestProvider(str): ...

        @Pid.module(providers=[TestProvider, FactoryDependency])
        class TestModule:
            def __init__(self, provider: TestProvider):
                self.provider = provider

        test_module = BootStrap.resolve(TestModule)

        assert isinstance(test_module.provider, str)
        assert test_module.provider == 'test_string'

    def test_factory_with_dependency_reassign(self):
        __store__ = {}

        @Pid.injectable()
        class FactoryDependency: ...

        def factory(provider: FactoryDependency):
            __store__['factory_provider'] = provider
            return TestProvider('test_string')

        @Pid.injectable(
            providers=[FactoryDependency],
            factory=factory
        )
        class TestProvider(str): ...

        @Pid.module(providers=[FactoryDependency, TestProvider])
        class TestModule:
            def __init__(self, provider: FactoryDependency):
                __store__['module_provider'] = provider

        BootStrap.resolve(TestModule)

        assert __store__['module_provider'] is not  __store__['factory_provider']


class TestsFactoryErrors:

    def test_factory_with_missed_dependency(self):
        @Pid.injectable()
        class FactoryDependency: ...

        def factory(dependency: FactoryDependency):
            assert dependency is not None
            return TestProvider('test_string')

        @Pid.injectable(
            factory=factory
        )
        class TestProvider(str): ...

        @Pid.module(providers=[TestProvider])
        class TestModule:
            def __init__(self, provider: TestProvider):
                self.provider = provider

        with pytest.raises(CannotResolveDependency):
            BootStrap.resolve(TestModule)


class TestsUnresolvedDependencies:

    def test_unresolved_dependency(self):
        @Pid.injectable()
        class TestProvider: ...

        @Pid.module(providers=[TestProvider])
        class TestModule:
            def __init__(self, provider: Provider[TestProvider]):
                assert isinstance(provider, Provider)
                assert provider._class is TestProvider

        BootStrap.resolve(TestModule)

    def test_unresolved_dependency_inherit(self):
        __store__ = {}

        @Pid.injectable()
        class SecondProvider: ...

        @Pid.injectable()
        class TestProvider:
            def __init__(self, provider: Provider[SecondProvider]):
                assert isinstance(provider, Provider)
                assert provider._class is SecondProvider

                __store__['provider_provider'] = provider

        @Pid.module(providers=[TestProvider, SecondProvider])
        class TestModule:
            def __init__(self, provider: Provider[SecondProvider]):
                assert isinstance(provider, Provider)
                assert provider._class is SecondProvider

                __store__['module_provider'] = provider

        BootStrap.resolve(TestModule)

        assert __store__['provider_provider'] is __store__['module_provider']

    def test_unresolved_dependency_resolve(self):
        @Pid.injectable()
        class TestProvider: ...

        @Pid.module(providers=[TestProvider])
        class TestModule:
            def __init__(self, provider: Provider[TestProvider]):
                resolved_provider = provider.resolve()

                assert not isinstance(resolved_provider, Provider)
                assert isinstance(resolved_provider, TestProvider)

        BootStrap.resolve(TestModule)

    def test_unresolved_dependency_resolve_self(self):
        @Pid.injectable()
        class TestProvider: ...

        @Pid.module(providers=[TestProvider])
        class TestModule:
            def __init__(self, provider: Provider[TestProvider]):
                resolved_provider = provider.resolve()

                assert not isinstance(resolved_provider, Provider)
                assert isinstance(resolved_provider, TestProvider)

        BootStrap.resolve(TestModule)

    def test_unresolved_dependency_resolve_with_tag(self):
        @Pid.injectable()
        class TestProvider: ...

        @Pid.module(providers=[TestProvider])
        class TestModule:
            def __init__(self, unresolved_provider: Provider[TestProvider], provider: TestProvider):
                resolved_provider = unresolved_provider.resolve('some_tag')

                assert resolved_provider is not provider
                assert isinstance(resolved_provider, TestProvider)

        BootStrap.resolve(TestModule)

    def test_unresolved_dependency_resolve_without_same_tag(self):
        @Pid.injectable()
        class TestProvider: ...

        @Pid.module(providers=[TestProvider])
        class TestModule:
            def __init__(self, unresolved_provider: Provider[TestProvider], provider: TestProvider):
                resolved_provider = unresolved_provider.resolve('some_tag')

                assert resolved_provider is not provider
                assert isinstance(resolved_provider, TestProvider)

        BootStrap.resolve(TestModule)

    def test_unresolved_dependency_provide_tag(self):
        __tag__ = 'some_tag'

        @Pid.injectable()
        class TestProvider: ...

        @Pid.module(providers=[TestProvider])
        class TestModule:
            def __init__(self, tag: Tag):
                assert tag == __tag__

        BootStrap.resolve(TestModule, tag=__tag__)

    def test_unresolved_dependency_child_provide_tag(self):
        __store__ = []
        __tag__ = 'some_tag'

        @Pid.injectable()
        class TestProvider:
            def __init__(self, tag: Tag):
                __store__.append(tag)

        @Pid.module(providers=[TestProvider])
        class TestModule:
            def __init__(self, unresolved_provider: Provider[TestProvider], _: TestProvider):
                unresolved_provider.resolve(__tag__)

        BootStrap.resolve(TestModule)

        first_tag, second_tag = __store__

        assert first_tag is None
        assert second_tag == __tag__

    def test_tag_implicit(self):
        __tag__ = 'some_tag'

        @Pid.injectable()
        class TestProvider: ...

        @Pid.module(providers=[TestProvider, Tag])
        class TestModule:
            def __init__(self, tag: Tag):
                assert __tag__ == tag

        BootStrap.resolve(TestModule, __tag__)
