from __future__ import annotations

from decorators import Providers



@Providers.injectable()
class SecondDep:
    a = 12


@Providers.module(
    providers=[
        SecondDep,
    ],
    exports=[
        SecondDep,
    ]
)
class SecondModule:
    def __init__(self, secondDep: SecondDep):
        print(secondDep)


@Providers.injectable()
class SomeDep:
    a = 12


@Providers.injectable()
class FourthDep:
    def __init__(self, someDep: SomeDep): ...


@Providers.injectable(providers=[SecondDep])
class ThirdDep:
    def __init__(self, fourth: FourthDep, SecondDep: SecondDep):
        print(SecondDep)


@Providers.module(
    imports=[SecondModule],
    providers=[
        SomeDep,
        ThirdDep,
        FourthDep,
    ]
)
class RootModule:
    def __init__(self, some: SomeDep, SecondDep: SecondDep):
        print(some.a)


module = RootModule.resolve()






# @Providers.injectable()
# class SomeDep:
#     a = 12
#
#
# @Providers.injectable(providers=[])
# class SomeProviderWithDep:
#     def __init__(self, someDep: SomeDep):
#         print(someDep)
#
#
# @Providers.module(
#     providers=[
#         SomeDep,
#         SomeProviderWithDep,
#     ],
#     exports=[
#         SomeDep,
#         SomeProviderWithDep
#     ],
# )
# class SomeModule:
#     def __init__(self, someProviderWithDep: SomeProviderWithDep, someDep: SomeDep):
#         print(someProviderWithDep)
#
#
# @Providers.module(
#     imports=[SomeModule],
#     providers=[
#         SomeProviderWithDep,
#     ]
# )
# class RootModule:
#     def __init__(self, someProviderWithDep: SomeProviderWithDep, someDep: SomeDep):
#         print(someProviderWithDep)
#
#
# RootModule.resolve()


# @Providers.injectable()
# class OmegaService:
#     a = 12
#
#
# @Providers.module(
#     providers=[OmegaService],
#     exports=[OmegaService]
# )
# class OmegaModule:
#     def __init__(self, OmegaService: OmegaService):
#         print('OmegaModule', OmegaService)
#
#
#
# @Providers.injectable()
# class BetaService:
#     def __init__(self, OmegaService: OmegaService):
#         print('BetaService', OmegaService)
#
# @Providers.module(
#     imports=[OmegaModule],
#     providers=[BetaService],
#     exports=[BetaService],
# )
# class BetaModule:
#     def __init__(self, OmegaService: OmegaService, BetaService: BetaService):
#         print('BetaModule', OmegaService, BetaService)
#
#
# @Providers.injectable()
# class AlphaService:
#     def __init__(self, OmegaService: OmegaService):
#         print('AlphaService', OmegaService)
#
#
# @Providers.module(
#     imports=[OmegaModule],
#     providers=[AlphaService],
#     exports=[AlphaService, OmegaService],
# )
# class AlphaModule:
#     def __init__(self, OmegaService: OmegaService, AlphaService: AlphaService):
#         print('AlphaModule', OmegaService, AlphaService)
#
#
# @Providers.module(
#     imports=[
#         AlphaModule,
#         BetaModule,
#     ],
#     providers=[
#         BetaService,
#     ]
# )
# class RootModule:
#     def __init__(self, BetaService: BetaService, AlphaService: AlphaService, OmegaService: OmegaService):
#         print('RootModule', BetaService, AlphaService, OmegaService)
#
#
# RootModule.resolve()


# @Providers.injectable()
# class OmegaService:
#     a = 12
#
#
# @Providers.module(
#     providers=[
#         OmegaService,
#     ],
#     exports=[
#         OmegaService
#     ],
# )
# class EndModule:
#     def __init__(self, OmegaService: OmegaService):
#         print(OmegaService)
#
#
# @Providers.module(
#     imports=[
#         EndModule
#     ],
#     exports=[
#         EndModule,
#     ],
# )
# class MiddleModule: ...
#
#
#
# @Providers.module(
#     imports=[
#         MiddleModule,
#     ],
#     providers=[
#     ]
# )
# class RootModule:
#     def __init__(self, OmegaService: OmegaService):
#         print(OmegaService)
#
#
# RootModule.resolve()
