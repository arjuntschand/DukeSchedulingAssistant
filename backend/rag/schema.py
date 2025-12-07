from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Literal


# Canonical major codes used for metadata filtering
MajorCode = Literal["ECE", "BME", "ME", "CEE_ENV", "CS", "ALL"]


@dataclass
class Document:
  id: str
  major: Optional[MajorCode]
  type: str
  code: Optional[str]
  title: Optional[str]
  text: str
  metadata: Dict[str, Any]

  def to_metadata(self) -> Dict[str, Any]:
    base = {
      "major": self.major,
      "type": self.type,
      "code": self.code,
      "title": self.title,
    }
    base.update(self.metadata)
    # Drop None values for cleaner filters
    return {k: v for k, v in base.items() if v is not None}


MAJOR_NAME_MAP: Dict[str, MajorCode] = {
  # Canonical codes
  "ECE": "ECE",
  "BME": "BME",
  "ME": "ME",
  "CEE_ENV": "CEE_ENV",
  "CS": "CS",
  "ALL": "ALL",
  # Human-readable labels from the frontend
  "ELECTRICAL & COMPUTER ENGINEERING": "ECE",
  "ELECTRICAL AND COMPUTER ENGINEERING": "ECE",
  "BIOMEDICAL ENGINEERING": "BME",
  "MECHANICAL ENGINEERING": "ME",
  "CIVIL & ENVIRONMENTAL ENGINEERING": "CEE_ENV",
  "CIVIL AND ENVIRONMENTAL ENGINEERING": "CEE_ENV",
  "COMPUTER SCIENCE": "CS",
}


def normalize_major(raw: Optional[str]) -> Optional[MajorCode]:
  if not raw:
    return None
  key = raw.strip().upper()
  return MAJOR_NAME_MAP.get(key)
