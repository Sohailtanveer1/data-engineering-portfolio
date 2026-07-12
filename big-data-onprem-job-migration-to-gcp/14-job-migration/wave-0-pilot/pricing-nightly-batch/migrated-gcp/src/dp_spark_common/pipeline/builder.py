"""
PipelineBuilder — see 07-spark-migration/08-oop-design-patterns.md
and 07-spark-migration/examples/job_builder.py (canonical source).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List


@dataclass
class PipelineContext:
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
    def __init__(self, context: PipelineContext, steps: List[_Step]):
        self._context = context
        self._steps = steps

    def run(self) -> PipelineContext:
        context = self._context
        for step in self._steps:
            context.logger.info("pipeline_step_started", extra={"step": step.name})
            context = step.func(context)
            context.logger.info("pipeline_step_completed", extra={"step": step.name})
        return context


class PipelineBuilder:
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
