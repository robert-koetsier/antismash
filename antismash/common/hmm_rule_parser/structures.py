# License: GNU Affero General Public License v3 or later
# A copy of GNU AGPL v3 should have been included in this software package in LICENSE.txt.

""" A collection of data structures for profile hits and profiles themselves
"""

import dataclasses
from typing import Any, Callable, Dict, List

from antismash.common.secmet import Record
from antismash.common.signature import Signature
from antismash.common.hmmscan_refinement import HSP


class ProfileHit:
    """ Minimum information for any hit generated by either HMMer profiles
        or dynamic profiles
    """
    def __init__(self, hit_id: str, query_id: str, bitscore: float, evalue: float, seeds: int = 0) -> None:
        self.hit_id = hit_id
        self.query_id = query_id
        self.bitscore = bitscore
        self.evalue = evalue
        self.seeds = seeds


class HMMerHit(ProfileHit):
    """ A HMMer-specific variant of ProfileHit """
    def __init__(self, hit_id: str, query_id: str, query_start: int, query_end: int,
                 seeds: int, evalue: float, bitscore: float) -> None:
        super().__init__(hit_id, query_id, bitscore, evalue, seeds)
        self.query_start = query_start
        self.query_end = query_end

    @classmethod
    def from_hsp(cls, hsp: HSP, seeds: int) -> "HMMerHit":
        """ Constructs an instance from an HSP """
        return cls(hsp.hit_id, hsp.query_id, hsp.query_start, hsp.query_end, seeds, hsp.evalue, hsp.bitscore)


class DynamicHit(ProfileHit):
    """ A variant of ProfileHit for dynamic profiles where scoring information
        may not be relevant
    """
    def __init__(self, cds_name: str, profile_name: str,
                 bitscore: float = 0., evalue: float = 1.) -> None:
        super().__init__(cds_name, profile_name, bitscore, evalue, seeds=0)


class DynamicProfile(Signature):
    """ A dynamic profile based on code, rather than a HMM """
    def __init__(self, name: str, description: str,
                 detect: Callable[[Record], Dict[str, List[DynamicHit]]]) -> None:
        super().__init__(name, "dynamic", description, 0, __file__)
        self._callable = detect

    def find_hits(self, record: Record) -> Dict[str, List[DynamicHit]]:
        """ Runs the profile over the record and return a dictionary mapping
            CDS name to a list of HSPs, one for each 'hit'
        """
        return self._callable(record)


@dataclasses.dataclass(frozen=True)
class Multipliers:
    """ Multipliers for use in scaling appropriate values within rules. """
    cutoff: float = 1.0
    neighbourhood: float = 1.0

    def __post_init__(self) -> None:
        if self.cutoff <= 0:
            raise ValueError("cutoff multiplier must be positive")
        if self.neighbourhood <= 0:
            raise ValueError("neighbourhood multiplier must be positive")

    def to_json(self) -> dict[str, Any]:
        """ Converts the instance to a JSON-friendly representation """
        return dataclasses.asdict(self)

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> "Multipliers":
        """ Rebuilds an instance from a JSON-friendly representation """
        return cls(**data)
