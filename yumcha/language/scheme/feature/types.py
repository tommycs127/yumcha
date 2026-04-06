from types import EllipsisType
from typing import Unpack

Feature = str | EllipsisType
FeatureTuple = tuple[Feature, ...]
FeatureTupleWithPrecedence = tuple[Unpack[FeatureTuple], bool]
FeatureDict = dict[FeatureTuple, FeatureTuple | FeatureTupleWithPrecedence]
InverseFeatureDict = dict[FeatureTuple, FeatureTuple]
