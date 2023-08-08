#!/usr/bin/python3
"""Website views file to process the request from the user.
"""

# Django modules
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordChangeView
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy

# Forms
from .forms import change_password as password_form, ProductsForm, ModulesForm
from .forms import update_user_profile as profile_update_form
from .forms import comp_update_auth as comp_update_auth
from .forms import TrainingForm, CommentForm

# Additional custom lib modules
from .py_files.competency.competency import *
from .py_files.iot_ta.code_review_api import *
from .py_files.iot_ta.iot_testcase import iot_testcase_op
from .py_files.common_lib.common import common_api
from .py_files.iot_ta.iot_environment import iot_environment
from .py_files.iot_ta.code_review_api import codereview_api
from Application.py_files.common_lib.decorators import iot_user
from .models import comments_field

class change_password(PasswordChangeView):
    """Password changing form validation and updation in database.
    
    URL : <site>/profile/change_password/

    TODO: Needs to be refactored into format similar to other functions.

    Args:
        PasswordChangeView : Password change view module from Django
    """
    form = password_form
    success_url = reverse_lazy('dashboard')

@login_required
def dashboard(request):
    """Render function for <site>/dashboard

    Args:
        request: User request to the page. 
    """
    return render(request, 'dashboard.html', {})

def login_user(request):
    """Render function for <site>/

    Args:
        request: User request to the page. 
    """
    if request.method == 'POST':
        username = request.POST['Username']
        password = request.POST['Password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('user_profile')
        else:
            messages.success(request, ("Invalid Credentials"))
            return redirect('login')
    if request.user.is_authenticated:
        return redirect('user_profile')
    else:
        return render(request, 'login_register.html')

@login_required
def logout_user(request):
    """Render function for logout

    URL : <site>/logout
    
    Args:
        request: User request to the page. 
    """

    logout(request)
    messages.success(request, ("You have been logged out."))
    return redirect('login')

@login_required
def user_profile(request):
    """Render function for user profile page.
    
    URL : <site>/profile

    Args:
        request: User request to the page. 
    """
    member = User.objects.all()

    # getting user profile instance 
    _user_id = request.user.id
    _user_f = User.objects.get(pk=_user_id)
    profile_form = profile_update_form(request.POST or None, instance=_user_f)
    
    comp_form = comp_update_auth(request.POST or None, instance=update_competency.objects.get(pk=2))

    if request.method == 'POST':
        if comp_form.is_valid():
            comp_form.save()
        if profile_form.is_valid():
            profile_form.save()
        return redirect('user_profile')
    return render(request, 'profile/profile.html', {'members': member, 'enable_update' : str(update_competency.objects.all()[0]), 'update_comp':comp_form, 'profile_form' : profile_form })

# *********************** IOT START **********************************
@iot_user
@login_required
def code_review_tracking(request):
    """Render function for IOT TA code review tracking page.

    URL : <site>/team/1/code_tracking/

    Args:
        request: User request to the page.
    """
    iot_class = codereview_api()
    iot_overall = iot_class.return_overall_for_all_iot_users(User)    
    context = {'overall' : iot_overall, 'user_details' : User.objects.all()}
    return render(request, 'teams/iot_ta/codereview.html', context)

@iot_user
@login_required
def iot_ta(request):
    """Render function for IOT TA team home page.
    
    URL : <site>/team/1

    Args:
        request: User request to the page. 
    """
    return render(request, 'teams/iot_ta/iot_home.html')

@iot_user
@login_required
def list_simu(request):
    """Render function for IOT TA test case summary page.

    URL : <site>/team/1/test_cases

    Args:
        request: User request to the page. 
    """
    iot_class = iot_environment()
    model = iot_class.get_ip_and_model_with_loc_for_all_simulators()
    counts = dict()
    iot_class = iot_testcase_op()
    for simu in iot_class.return_available_simulators():
        counts[simu] = iot_class.get_counts_of_cases(iot_class.organise_simuwise_with_catagories(simu))
    counts['total'] = iot_class.get_counts_of_cases(iot_class.categorise_iot_testcase())
    if request.method == 'POST':
        common_api().update_latest_branch('/Application/static/resources/iot/rellab_iot')
        return redirect('simu_lists')

    context = {'counts': counts, 'model' : model, 'bug_and_ntrdy': iot_class.segregate_bug_and_not_ready_cases(),
                'owners': iot_class.fetch_owners_of_test_cases(), 'simuwise_bug_and_ntrdy' : iot_class.simuwise_bug_and_not_ready_cases(),
                'case_id': iot_class.fetch_gid_number_of_case()}
    return render(request, 'teams/iot_ta/cases/list_simulators.html', context)

@iot_user
@login_required
def live_environments(request):
    """Render function for IOT TA live environment page.

    URL : <site>/team/1/environments/

    Args:
        request: User request to the page.
    """
    iot_class =  iot_environment()
    configs = iot_class.simulator_wise_device_identifiers()
    _live_status = iot_class.get_status_for_device_identifiers()
    desc_here = iot_class.get_ip_and_model_with_loc_for_all_simulators()
    context = {
        'configurations': configs, 'desc': desc_here, 'live_data': _live_status}
    return render(request, 'teams/iot_ta/environment_view.html', context)

@iot_user
@login_required
def simu_cases(request, simu):
    """Render function for each available simulators.

    URL : <site>/team/1/test_cases/<simulator>

    Args:
        request: User request to the page.
        simu (str): Simulator ID to return respective test cases. eg: SIMU144.
    """

    comment_form = CommentForm(request.POST)
    case_id = request.POST.get("case_id")
    comment = request.POST.get("comment")
    if comment:
        existing_comment = comments_field.objects.filter(case_id=case_id).first()
        if existing_comment:
            existing_comment.comments = comment
            existing_comment.save()
        else:
            new_comment = comment_form.save(commit=False)
            new_comment.case_id = case_id
            new_comment.comments = comment
            new_comment.save()

    iot_class = iot_testcase_op()
    counts = dict()
    for _simu in iot_class.return_available_simulators():
        counts[_simu] = iot_class.get_counts_of_cases(iot_class.organise_simuwise_with_catagories(_simu))
    counts['total'] = iot_class.get_counts_of_cases(iot_class.categorise_iot_testcase())
    if simu == 'Total':
        content = iot_class.categorise_iot_testcase()
        simu = 'total'
    else:
        content = iot_class.organise_simuwise_with_catagories(str(simu))
    comment_field = comments_field.objects.all()
    iot_testcase_op.add_simulator_name('Overall Repository' if simu=='total' else str(simu),content)
    context = {'content': content,'comments_field':comment_field,'comment':comment,
               'comment_form': comment_form,
               'name': 'Overall Repository' if simu=='total' else str(simu),
               'filter_case': iot_class.segregate_bug_and_not_ready_cases(),
               'counts': counts[str(simu)],
               'docs': iot_class.fetch_documentation_of_test_cases(),
               'owners': iot_class.fetch_owners_of_test_cases(),
               'case_id': iot_class.fetch_gid_number_of_case()}
    return render(request, 'teams/iot_ta/cases/cases.html', context)

@iot_user
@login_required
def export_excel(request, simu):
    """On request to download excel file of test cases.
    """
    filename = "Application/static/iot.xlsx"  # this is the file people must download
    with open(filename, 'rb') as f:
        response = HttpResponse(f.read(), content_type='static/iot.xlsx')
        response['Content-Disposition'] = 'attachment; filename='+ f'{simu}.xlsx'
        response['Content-Type'] = 'application/vnd.ms-excel; charset=utf-16'
        return response

# *********************** IOT END **********************************

# ******************* COMPETENCY START *****************************

@login_required
def competency_members(request):
    """Render function for available competency user listing.

    URL : <site>/competency

    Args:
        request: User request to the page.
    """
    if request.user.is_manager:
        members = User.objects.all()
        # Convert objects to dictionaries of item.
        _required = dict()
        for member in members:
            _name = member.first_name + ' ' + member.last_name
            _required[_name] = member.designation
        context = {'members': _required, 'modified_date' : get_last_modified_of_all_users(members)}
        return render(request, 'competency/all_members.html', context)
    return redirect('dashboard')

@login_required
def competency_view(request):
    """Render function for Competency view of logged in user 

    URL : <site>/competency/view/

    Args:
        request: User request to the page.
    """
    update_user_and_modules()
    user = request.user
    user = str(user.first_name)+' '+str(user.last_name)
    comp = extract_data_from_excel(user)
    _last_modified_date = get_last_modified_time(user)
    context = {'user_selected' : user, 'competency' : comp, 'modified_date': _last_modified_date}
    return render(request, 'competency/competency_view.html', context)

@login_required
def competency_view_user(request, individual):
    """Render function for Competency view for all selected users only applicable for manager.

    URL : <site>/competency/view/<str:individual>

    Args:
        request: User request to the page.
        individual (str): username of the user.
    """
    update_user_and_modules()
    if request.user.is_manager:
        for user in User.objects.all():
            user = str(user.first_name) + ' ' + str(user.last_name)
            if str(user) == individual:
                comp = extract_data_from_excel(user)
                _last_modified_date = get_last_modified_time(user)
                context = {'user_selected' : user, 'competency' : comp, 'modified_date': _last_modified_date}
                return render(request, 'competency/competency_view.html', context)
    return competency_view(request)

@login_required
def competency_update_form(request):
    """Render function for Competency update form, Module form and Product form from profile

    URL : <site>/profile/comp_update/

    Args:
        request: User request to the page.
    """
    update_user_and_modules()
    product_form = ProductsForm()
    module_form = ModulesForm()
    if str(update_competency.objects.all()[0]) == 'Enable':
        context = {'product_form': product_form, 'ModulesForm': ModulesForm, 'ProductsForm': ProductsForm, 'modules': module.objects.all(),
                    'products': product.objects.all(), 'user_comp': extract_data_from_excel(str(request.user.first_name)+' '+str(request.user.last_name)),
                   'module_form': module_form}
        if request.method == 'POST':
            if request.POST.get('submit_product') == 'Update Product':
                product_form = ProductsForm(request.POST)
                if product_form.is_valid():
                    product_form.save()
                    messages.success(request, "You have updated Products form successfully")
                    update_user_and_modules()
                    return redirect('comp_update_form')
            elif request.POST.get('submit_module') == 'Update Module':
                module_form = ModulesForm(request.POST)
                if module_form.is_valid():
                    module_form.save()
                    messages.success(request, "You have updated Modules form successfully")
                    update_user_and_modules()
                    return redirect('comp_update_form')
            else:
                values = {}
                for mod in module.objects.all():
                    values[str(mod)] = {}
                    for prod in product.objects.all():
                        if str(prod.module) == str(mod):
                            values[str(mod)][str(prod)] = [request.POST[f'current_{str(prod)}'],
                                                           request.POST[f'target_{str(prod)}']]
                user = request.user.first_name + ' ' + request.user.last_name
                update_modified_time(user)
                add_update_competency(values, user)
                messages.success(request, "You have updated Competency successfully")
                return redirect('user_profile')
        return render(request, 'profile/competency_update.html', context)
    return redirect('dashboard')

@login_required()
def competency_delete_form(request, module_id):
    """Render function for Competency deleting module form from update form

    URL : <site>/profile/delete_module/<module_id>

    Args:
        request: User request to the page.
        module_id (str): id of each module


    """
    m = module.objects.get(pk=module_id)
    delete_modules(module_id)
    m.delete()
    update_user_and_modules()
    return redirect('comp_update_form')

@login_required()
def competency_p_delete_form(request, product_id):
    """Render function for Competency deleting Product form from update form

    URL : <site>/profile/delete_product/<product_id>

    Args:
        request: User request to the page.
        product_id (str): id of each product
    """
    p = product.objects.get(pk=product_id)
    delete_products(product_id)
    p.delete()
    update_user_and_modules()
    return redirect('comp_update_form')

@login_required
def export_excel_cm(request):
    """On request to download excel file of Competency Matrix.
    
    Args:
        request: User request to the page.
    """
    filename = "Application/static/db.xlsx"  # this is the file people must download
    with open(filename, 'rb') as f:
        response = HttpResponse(f.read(), content_type='static/db.xlsx')
        response['Content-Disposition'] = 'attachment; filename=' + f'Competency Matrix.xlsx'
        response['Content-Type'] = 'application/vnd.ms-excel; charset=utf-16'
        return response

@login_required
def training_list(request):
    """Render function for training list page

    URL : <site>/competency/training_list

    Args:
        request: User request to the page.
    """
    _trainings_list = training.objects.all()
    _filtered_trainings = filter_trainings(_trainings_list)
    context = {'trainings': _filtered_trainings}
    return render(request, 'competency/training_list.html', context)
@login_required
def add_training(request):
    """Render function for add trainings in database

    URL : <site>/competency/add_training

    Args:
        request: User request to the page.
    """
    training_form = TrainingForm()
    context = {'add_training': training_form}
    if request.method == 'POST':
        training_form = TrainingForm(request.POST)
        if training_form.is_valid():
            training_form.save()
            return redirect('training_list')
    return render(request, 'competency/add_training.html', context)

# ******************* COMPETENCY END *****************************

# ******************* PROCESS AUDIT START *****************************

@login_required
def process_home(request):
    """Render function for process audit home page

    URL : <site>/process

    Args:
        request: User request to the page.
    """
    return render(request, 'process_audit/process_home.html')

# ******************* PROCESS AUDIT END *****************************
