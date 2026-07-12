"""
PipelineBuilder — Builder pattern reference implementation.

Belongs in: dp_spark_common/pipeline/builder.py (shared library)
See: 07-spark-migration/08-oop-design-patterns.md

Assembles a job's pipeline as an explicit, readable, named sequence of
steps, each a plain function taking and returning a PipelineContext. This
is what makes individual steps trivially unit-testable in isolation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


@dataclass
class PipelineContext:
    """
    Carries the pipeline's current state (DataFrames and metadata) between
    steps. Steps read what they need from `data` and return an updated
    context — never mutate shared global state.
    """

    spark: Any
    config: Any
    logger: Any
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


StepFunc = Callable[[PipelineContext], PipelineContext]


@dataclass
class _Step:
    name: str
    func: StepFunc


class Pipeline:
    """Runs an ordered list of steps, logging progress and timing each one."""

    def __init__(self, context: PipelineContext, steps: List[_Step]):
        self._context = context
        self._steps = steps

    def run(self) -> PipelineContext:
        context = self._context
        for step in self._steps:
            context.logger.info(f"pipeline_step_started", extra={"step": step.name})
            context = step.func(context)
            context.logger.info(f"pipeline_step_completed", extra={"step": step.name})
        return context


class PipelineBuilder:
    """Fluent builder assembling a job's pipeline as a named step sequence."""

    def __init__(self, spark: Any, config: Any, logger: Any):
        self._context = PipelineContext(spark=spark, config=config, logger=logger)
        self._steps: List[_Step] = []

    def add_step(self, name: str, func: StepFunc) -> "PipelineBuilder":
        self._steps.append(_Step(name=name, func=func))
        return self

    def build(self) -> Pipeline:
        if not self._steps:
            raise ValueError("Cannot build a pipeline with zero steps")
        return Pipeline(context=self._context, steps=self._steps)
