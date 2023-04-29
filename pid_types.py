from typing import Type

from provider import Provider


ProviderType = Provider | Type
ProvidersType = list[ProviderType]
