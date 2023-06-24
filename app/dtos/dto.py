from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class DTO(ABC):

    @abstractmethod
    def to_db_model(self):
        """Map DTO object to DB model"""
