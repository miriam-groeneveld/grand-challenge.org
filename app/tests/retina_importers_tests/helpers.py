from io import BytesIO
from pathlib import Path
import json
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework.authtoken.models import Token
from tests.factories import UserFactory
from tests.cases_tests.factories import ImageFactory, ImageFactoryWithImageFile
from tests.studies_tests.factories import StudyFactory
from tests.patients_tests.factories import PatientFactory
from tests.archives_tests.factories import ArchiveFactory
from grandchallenge.studies.models import Study
from tests.cases_tests import RESOURCE_PATH
from grandchallenge.subdomains.utils import reverse


def get_retina_user_with_token(is_retina_user=True, **user_kwargs):
    user = UserFactory(**user_kwargs)
    if is_retina_user:
        grader_group, group_created = Group.objects.get_or_create(
            name=settings.RETINA_GRADERS_GROUP_NAME
        )
        grader_group.user_set.add(user)

    token = Token.objects.create(user=user)
    return user, token.key


def get_auth_token_header(user, token=None):
    """
    Retrieve auth token that can be inserted into client request for authentication
    :param user: "staff" for staff user, "normal" for normal user, else AnonymousUser
    :param token: (optional) authentication token, `user` is not used if this is defined
    :return:
    """
    if token is None:
        if user == "staff":
            _, token = get_retina_user_with_token(is_staff=True)
        elif user == "normal":
            _, token = get_retina_user_with_token()
        elif user == "import_user":
            user = get_user_model().objects.get(
                username=settings.RETINA_IMPORT_USER_NAME
            )
            token_obj = Token.objects.create(user=user)
            token = token_obj.key

    auth_header = {}
    if token:
        auth_header.update({"HTTP_AUTHORIZATION": "Token " + token})

    return auth_header


# helper functions
def create_test_images():
    """
    Create image for testing purposes
    :return: file
    """
    files = {}
    for file_type in ("mhd", "zraw"):
        files[file_type] = BytesIO()
        with open(RESOURCE_PATH / f"image5x6x7.{file_type}", "rb") as fh:
            files[file_type].name = fh.name
            files[file_type].write(fh.read())
        files[file_type].seek(0)

    return files


def read_json_file(path_to_file):
    path_to_file = (
        Path("/app/tests/retina_importers_tests/test_data") / path_to_file
    )
    print(path_to_file.absolute())
    try:
        file = open(path_to_file, "r")
        if file.mode == "r":
            file_contents = file.read()
            file_object = json.loads(file_contents)
            return file_object
        else:
            raise FileNotFoundError()
    except FileNotFoundError:
        print(f"Warning: No json file in {path_to_file}")
    return None


def create_upload_image_test_data(data_type="default", with_image=True):
    # create image
    files = create_test_images()
    if data_type == "kappa":
        data = read_json_file("upload_image_valid_data_kappa.json")
    elif data_type == "areds":
        data = read_json_file("upload_image_valid_data_areds.json")
    else:
        data = read_json_file("upload_image_valid_data.json")

    if with_image:
        # create request payload
        data.update({"image_hd": files["mhd"], "image_raw": files["zraw"]})
    return data


def create_upload_image_invalid_test_data(data_type="default"):
    # create image
    files = create_test_images()
    if data_type == "kappa":
        data = read_json_file("upload_image_invalid_data_kappa.json")
    elif data_type == "areds":
        data = read_json_file("upload_image_invalid_data_areds.json")
    else:
        data = read_json_file("upload_image_invalid_data.json")
    # create request payload
    data.update({"image_hd": files["mhd"], "image_raw": files["zraw"]})
    return data


def remove_test_image(response):
    # Remove uploaded test image from filesystem
    response_obj = json.loads(response.content)
    full_path_to_image = settings.APPS_DIR / Path(
        response_obj["image"]["image"][1:]
    )
    Path.unlink(full_path_to_image)


def get_response_status(
    client, reverse_name, data, user="anonymous", annotation_data=None
):
    auth_header = get_auth_token_header(user)
    url = reverse(reverse_name)

    if annotation_data:
        # create objects that need to exist in database before request is made
        patient = PatientFactory(name=data.get("patient_identifier"))
        existing_models = {"studies": [], "series": [], "images": []}
        images = []
        for data_row in data.get("data"):
            if (
                data_row.get("study_identifier")
                not in existing_models["studies"]
            ):
                study = StudyFactory(
                    name=data_row.get("study_identifier"), patient=patient
                )
                existing_models["studies"].append(study.name)
            else:
                study = Study.objects.get(
                    name=data_row.get("study_identifier")
                )

            if (
                data_row.get("image_identifier")
                not in existing_models["images"]
            ):
                image = ImageFactory(
                    name=data_row.get("image_identifier"), study=study
                )
                existing_models["images"].append(image.name)
                images.append(image)
        archive = ArchiveFactory(
            name=data.get("archive_identifier"), images=images
        )

        response = client.post(
            url,
            data=json.dumps(data),
            content_type="application/json",
            **auth_header,
        )
    else:
        response = client.post(url, data=data, **auth_header)
    return response.status_code


def create_element_spacing_request(
    client,
    image_name=None,
    user="import_user",
    study=None,
    es=None,
    is_3d=False,
):
    auth_header = get_auth_token_header(user)
    url = reverse("retina:importers:set-element-spacing-for-image")
    request_data = {}

    if image_name is not None:
        request_data["image_identifier"] = image_name
    else:
        image = ImageFactoryWithImageFile()
        request_data["image_identifier"] = image.name

    if is_3d:
        request_data["sub_image_name"] = "oct"

    if es is not None:
        request_data["element_spacing_x"] = es[0]
        request_data["element_spacing_y"] = es[1]
        if is_3d:
            request_data["element_spacing_z"] = es[2]
    else:
        request_data["element_spacing_x"] = 10
        request_data["element_spacing_y"] = 10
        if is_3d:
            request_data["element_spacing_z"] = 10

    if study is not None:
        request_data["study_identifier"] = study.name

    data = json.dumps(request_data)

    return client.post(
        url, data=data, content_type="application/json", **auth_header
    )
