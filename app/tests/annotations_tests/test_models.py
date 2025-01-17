import pytest
from django.db import IntegrityError
from guardian.shortcuts import get_perms

from tests.annotations_tests.factories import (
    ETDRSGridAnnotationFactory,
    MeasurementAnnotationFactory,
    BooleanClassificationAnnotationFactory,
    IntegerClassificationAnnotationFactory,
    CoordinateListAnnotationFactory,
    PolygonAnnotationSetFactory,
    SinglePolygonAnnotationFactory,
    LandmarkAnnotationSetFactory,
    SingleLandmarkAnnotationFactory,
    ImageQualityAnnotationFactory,
    ImagePathologyAnnotationFactory,
    RetinaImagePathologyAnnotationFactory,
)
from tests.model_helpers import do_test_factory
from tests.viewset_helpers import get_user_from_user_type


@pytest.mark.django_db
class TestAnnotationModels:
    def test_default_model_str(self):
        etdrs = ETDRSGridAnnotationFactory()
        assert str(etdrs) == "<{} by {} on {} for {}>".format(
            etdrs.__class__.__name__,
            etdrs.grader.username,
            etdrs.created.strftime("%Y-%m-%d at %H:%M:%S"),
            etdrs.image,
        )

    def test_measurement_duplicate_not_allowed(self):
        measurement = MeasurementAnnotationFactory()
        try:
            measuremt_duplicate = MeasurementAnnotationFactory(
                image=measurement.image,
                grader=measurement.grader,
                created=measurement.created,
                start_voxel=measurement.start_voxel,
                end_voxel=measurement.end_voxel,
            )
            pytest.fail(
                "No integrity error when submitting duplicate measurement annotation"
            )
        except IntegrityError:
            pass


@pytest.mark.parametrize(
    "user_type",
    [
        "normal_user",
        "retina_grader_non_allowed",
        "retina_grader",
        "retina_admin",
    ],
)
@pytest.mark.django_db
class TestPermissions:
    def test_single_model_permissions(
        self, TwoRetinaPolygonAnnotationSets, user_type
    ):
        user = get_user_from_user_type(
            user_type, grader=TwoRetinaPolygonAnnotationSets.grader1
        )
        perms = get_perms(
            user,
            TwoRetinaPolygonAnnotationSets.polygonset1.singlepolygonannotation_set.first(),
        )
        default_permissions = (
            TwoRetinaPolygonAnnotationSets.polygonset1.singlepolygonannotation_set.first()._meta.default_permissions
        )
        for permission_type in default_permissions:
            if user_type == "retina_grader_non_allowed":
                assert (
                    f"{permission_type}_singlepolygonannotation" not in perms
                )
            else:
                assert f"{permission_type}_singlepolygonannotation" in perms

    def test_model_permissions(
        self, TwoRetinaPolygonAnnotationSets, user_type
    ):
        user = get_user_from_user_type(
            user_type, grader=TwoRetinaPolygonAnnotationSets.grader1
        )
        perms = get_perms(user, TwoRetinaPolygonAnnotationSets.polygonset1)
        default_permissions = (
            TwoRetinaPolygonAnnotationSets.polygonset1._meta.default_permissions
        )
        for permission_type in default_permissions:
            if user_type == "retina_grader_non_allowed":
                assert f"{permission_type}_polygonannotationset" not in perms
            else:
                assert f"{permission_type}_polygonannotationset" in perms


@pytest.mark.django_db
@pytest.mark.parametrize(
    "factory",
    (
        ETDRSGridAnnotationFactory,
        MeasurementAnnotationFactory,
        BooleanClassificationAnnotationFactory,
        IntegerClassificationAnnotationFactory,
        CoordinateListAnnotationFactory,
        PolygonAnnotationSetFactory,
        SinglePolygonAnnotationFactory,
        LandmarkAnnotationSetFactory,
        SingleLandmarkAnnotationFactory,
        ImageQualityAnnotationFactory,
        ImagePathologyAnnotationFactory,
        RetinaImagePathologyAnnotationFactory,
    ),
)
class TestFactories:
    def test_factory_creation(self, factory):
        do_test_factory(factory)
