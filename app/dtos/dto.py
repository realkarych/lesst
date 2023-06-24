from __future__ import annotations

from dataclasses import dataclass

from abc import ABC, abstractmethod


@dataclass(frozen=True)
class DTO(ABC):

    @abstractmethod
    def to_db_model(self):
        """Map DTO object to DB model"""
