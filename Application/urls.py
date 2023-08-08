from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required
from .forms import change_password

urlpatterns = [
    path('', views.login_user, name="login"),
    path('logout', views.logout_user, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),

    path('team/1', views.iot_ta, name='iot_ta'),
    path('team/1/test_cases', views.list_simu, name='simu_lists'),
    path('team/1/test_cases/<str:simu>', views.simu_cases, name='simu_cases'),
    path('team/1/environments/', views.live_environments, name='environments'),
    path('team/1/code_tracking/', views.code_review_tracking, name='code_tracking'),
    path('export_excel/<str:simu>', views.export_excel, name="iot_excel"),

    path('competency/', views.competency_members, name="competency"),
    path('competency/trainings/', views.training_list, name="training_list"),
    path('competency/add_training/', views.add_training, name="add_training"),
    path('competency/view/', views.competency_view, name="competency_view"),
    path('competency/view/<str:individual>', views.competency_view_user, name="competency_view_user"),
    path('export_excel_cm', views.export_excel_cm, name="cm_excel"),

    path('profile/', views.user_profile, name='user_profile'),
    path('profile/comp_update/', views.competency_update_form, name='comp_update_form'),
    path('profile/delete_module/<module_id>', views.competency_delete_form, name='comp_delete_form'),
    path('profile/delete_product/<product_id>', views.competency_p_delete_form, name='comp_p_delete_form'),
    path('profile/change_password/', views.change_password.as_view(
        template_name='profile/change_password.html',form_class=change_password), name='update_password'),

    path('process', views.process_home, name='process_home'),
]