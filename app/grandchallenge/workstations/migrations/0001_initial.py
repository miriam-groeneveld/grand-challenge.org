# Generated by Django 2.1.8 on 2019-04-10 16:12

import datetime
from decimal import Decimal
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields
import grandchallenge.challenges.models
import grandchallenge.container_exec.models
import grandchallenge.core.storage
import grandchallenge.core.validators
import simple_history.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name="HistoricalSession",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        db_index=True, default=uuid.uuid4, editable=False
                    ),
                ),
                ("created", models.DateTimeField(blank=True, editable=False)),
                ("modified", models.DateTimeField(blank=True, editable=False)),
                (
                    "status",
                    models.PositiveSmallIntegerField(
                        choices=[
                            (0, "Queued"),
                            (1, "Started"),
                            (2, "Running"),
                            (3, "Failed"),
                            (4, "Stopped"),
                        ],
                        default=0,
                    ),
                ),
                (
                    "maximum_duration",
                    models.DurationField(default=datetime.timedelta(0, 600)),
                ),
                ("user_finished", models.BooleanField(default=False)),
                (
                    "history_id",
                    models.AutoField(primary_key=True, serialize=False),
                ),
                ("history_date", models.DateTimeField()),
                (
                    "history_change_reason",
                    models.CharField(max_length=100, null=True),
                ),
                (
                    "history_type",
                    models.CharField(
                        choices=[
                            ("+", "Created"),
                            ("~", "Changed"),
                            ("-", "Deleted"),
                        ],
                        max_length=1,
                    ),
                ),
                (
                    "creator",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "history_user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "historical session",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": "history_date",
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name="Session",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("modified", models.DateTimeField(auto_now=True)),
                (
                    "status",
                    models.PositiveSmallIntegerField(
                        choices=[
                            (0, "Queued"),
                            (1, "Started"),
                            (2, "Running"),
                            (3, "Failed"),
                            (4, "Stopped"),
                        ],
                        default=0,
                    ),
                ),
                (
                    "maximum_duration",
                    models.DurationField(default=datetime.timedelta(0, 600)),
                ),
                ("user_finished", models.BooleanField(default=False)),
                (
                    "creator",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="Workstation",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("modified", models.DateTimeField(auto_now=True)),
                (
                    "title",
                    models.CharField(max_length=255, verbose_name="title"),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True, null=True, verbose_name="description"
                    ),
                ),
                (
                    "slug",
                    django_extensions.db.fields.AutoSlugField(
                        blank=True,
                        editable=False,
                        populate_from="title",
                        verbose_name="slug",
                    ),
                ),
                (
                    "logo",
                    models.ImageField(
                        upload_to=grandchallenge.challenges.models.get_logo_path
                    ),
                ),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="WorkstationImage",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("modified", models.DateTimeField(auto_now=True)),
                (
                    "staged_image_uuid",
                    models.UUIDField(blank=True, editable=False, null=True),
                ),
                (
                    "image",
                    models.FileField(
                        blank=True,
                        help_text=".tar.gz archive of the container image produced from the command 'docker save IMAGE | gzip -c > IMAGE.tar.gz'. See https://docs.docker.com/engine/reference/commandline/save/",
                        storage=grandchallenge.core.storage.PrivateS3Storage(),
                        upload_to=grandchallenge.container_exec.models.docker_image_path,
                        validators=[
                            grandchallenge.core.validators.ExtensionValidator(
                                allowed_extensions=(".tar", ".tar.gz")
                            )
                        ],
                    ),
                ),
                (
                    "image_sha256",
                    models.CharField(editable=False, max_length=71),
                ),
                (
                    "ready",
                    models.BooleanField(
                        default=False,
                        editable=False,
                        help_text="Is this image ready to be used?",
                    ),
                ),
                ("status", models.TextField(editable=False)),
                ("requires_gpu", models.BooleanField(default=False)),
                (
                    "requires_gpu_memory_gb",
                    models.PositiveIntegerField(default=4),
                ),
                ("requires_memory_gb", models.PositiveIntegerField(default=4)),
                (
                    "requires_cpu_cores",
                    models.DecimalField(
                        decimal_places=2, default=Decimal("1.0"), max_digits=4
                    ),
                ),
                (
                    "http_port",
                    models.PositiveIntegerField(
                        default=8080,
                        validators=[
                            django.core.validators.MaxValueValidator(65535)
                        ],
                    ),
                ),
                (
                    "websocket_port",
                    models.PositiveIntegerField(
                        default=4114,
                        validators=[
                            django.core.validators.MaxValueValidator(65535)
                        ],
                    ),
                ),
                (
                    "initial_path",
                    models.CharField(
                        blank=True,
                        default="Applications/GrandChallengeViewer/index.html",
                        max_length=256,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="This path is invalid, it must not start with a /",
                                regex="^(?:[^/][^\\s]*)\\Z",
                            )
                        ],
                    ),
                ),
                (
                    "creator",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "workstation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="workstations.Workstation",
                    ),
                ),
            ],
            options={"abstract": False},
        ),
        migrations.AddField(
            model_name="session",
            name="workstation_image",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="workstations.WorkstationImage",
            ),
        ),
        migrations.AddField(
            model_name="historicalsession",
            name="workstation_image",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="workstations.WorkstationImage",
            ),
        ),
    ]
