"""Design boundary for future parsers; no production parsers or downloads are installed."""

from typing import Literal, Protocol, Self

from pydantic import model_validator

from infinite_engine.catalog.contracts import Contract, Text
from infinite_engine.sources.contracts import AdapterKind, ArtifactEntry, SourceDocument


class ParseIssue(Contract):
    locator: Text
    message: Text


class ParseResult(Contract):
    status: Literal["complete", "partial", "failed"]
    anchors: tuple[ArtifactEntry, ...] = ()
    issues: tuple[ParseIssue, ...] = ()
    # Output is metadata/anchors, never verified Claim objects.

    @model_validator(mode="after")
    def coherent_result(self) -> Self:
        if any(a.payload.kind != "source_anchor" for a in self.anchors):
            raise ValueError("Parse results contain only anchors")
        if self.status == "complete" and self.issues:
            raise ValueError("Complete results cannot hide parse issues")
        if self.status != "complete" and not self.issues:
            raise ValueError("Partial/failed results require localized issues")
        if self.status == "failed" and self.anchors:
            raise ValueError("Retained successful anchors require partial status")
        if self.status == "partial" and not self.anchors:
            raise ValueError("Partial results must retain successful anchors")
        return self


class SourceAdapter(Protocol):
    kind: AdapterKind

    def parse(self, content: bytes, document: SourceDocument) -> ParseResult:
        """Parse caller-supplied authorized bytes; preserve native locators and failures."""
        ...
