# -*- coding: utf-8 -*-
from pathlib import Path

from ckeditor.fields import RichTextField
from django.db import models
from social_django.fields import JSONField

from grandchallenge.core.models import (
    UUIDModel, CeleryJobModel, DockerImageModel
)
from grandchallenge.core.urlresolvers import reverse
from grandchallenge.evaluation.backends.dockermachine.evaluator import \
    Evaluator


class Algorithm(UUIDModel, DockerImageModel):
    description_html = RichTextField(blank=True)

    def get_absolute_url(self):
        return reverse("algorithms:detail", kwargs={"pk": self.pk})


class AlgorithmExecutor(Evaluator):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            results_file=Path("/output/results.json"),
            **kwargs
        )


class Job(UUIDModel, CeleryJobModel):
    algorithm = models.ForeignKey(Algorithm, on_delete=models.CASCADE)
    case = models.ForeignKey("cases.Case", on_delete=models.CASCADE)

    @property
    def container(self):
        return self.algorithm

    @property
    def input_files(self):
        return [c.file for c in self.case.casefile_set.all()]

    @property
    def evaluator_cls(self):
        return AlgorithmExecutor

    def get_absolute_url(self):
        return reverse("algorithms:jobs-detail", kwargs={"pk": self.pk})


class Result(UUIDModel):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    output = JSONField(default=dict)

    def get_absolute_url(self):
        return reverse("algorithms:results-detail", kwargs={"pk": self.pk})
