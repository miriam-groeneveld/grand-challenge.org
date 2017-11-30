from django.conf.urls import url

from evaluation.forms import test_upload_widget, test_upload_widget2
from evaluation.views import uploader_widget_test, MethodCreate, \
    SubmissionCreate, \
    JobCreate, MethodList, SubmissionList, JobList, ResultList, MethodDetail, \
    SubmissionDetail, JobDetail, ResultDetail, EvaluationAdmin

urlpatterns = [
    url(r'^$', EvaluationAdmin.as_view(), name='home'),

    url(r'^methods/$', MethodList.as_view(), name='method-list'),
    url(r'^methods/create/$', MethodCreate.as_view(), name='method-create'),
    url(r'^methods/(?P<pk>[0-9a-fA-F-]+)/$', MethodDetail.as_view(),
        name='method-detail'),

    url(r'^submissions/$', SubmissionList.as_view(), name='submission-list'),
    url(r'^submissions/create/$', SubmissionCreate.as_view(),
        name='submission-create'),
    url(r'^submissions/(?P<pk>[0-9a-fA-F-]+)/$', SubmissionDetail.as_view(),
        name='submission-detail'),

    url(r'^jobs/$', JobList.as_view(), name='job-list'),
    url(r'^jobs/create/$', JobCreate.as_view(), name='job-create'),
    url(r'^jobs/(?P<pk>[0-9a-fA-F-]+)/$', JobDetail.as_view(),
        name='job-detail'),

    url(r'^results/$', ResultList.as_view(), name='result-list'),
    url(r'^results/(?P<pk>[0-9a-fA-F-]+)/$', ResultDetail.as_view(),
        name='result-detail'),

    url(f'^{test_upload_widget.ajax_target_path}',
        test_upload_widget.handle_ajax),
    url(f'^{test_upload_widget2.ajax_target_path}',
        test_upload_widget2.handle_ajax),
    url(r'^testwidget', uploader_widget_test),
]
