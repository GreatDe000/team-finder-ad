from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET

from projects.views import query_prefix

from .forms import LoginForm, ProfileForm, RegisterForm, TeamFinderPasswordChangeForm
from .models import User


def paginate(request, queryset, per_page=12):
    return Paginator(queryset, per_page).get_page(request.GET.get("page"))


def register(request):
    if request.user.is_authenticated:
        return redirect("projects:list")
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("users:login")
    else:
        form = RegisterForm()
    return render(request, "users/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("projects:list")
    if request.method == "POST":
        form = LoginForm(request, request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect("projects:list")
    else:
        form = LoginForm(request)
    return render(request, "users/login.html", {"form": form})


@require_GET
def logout_view(request):
    logout(request)
    return redirect("projects:list")


@require_GET
def user_detail(request, pk):
    profile_user = get_object_or_404(User.objects.prefetch_related("owned_projects"), pk=pk)
    return render(request, "users/user-details.html", {"user": profile_user})


@login_required
def edit_profile(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("users:detail", pk=request.user.pk)
    else:
        form = ProfileForm(instance=request.user)
    return render(request, "users/edit_profile.html", {"form": form})


@login_required
def change_password(request):
    if request.method == "POST":
        form = TeamFinderPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect("users:detail", pk=request.user.pk)
    else:
        form = TeamFinderPasswordChangeForm(request.user)
    return render(request, "users/change_password.html", {"form": form})


@require_GET
def users_list(request):
    users = User.objects.all().prefetch_related("owned_projects").order_by("-id")
    active_filter = request.GET.get("filter") if request.user.is_authenticated else None
    if active_filter == "owners-of-favorite-projects":
        users = User.objects.filter(
            owned_projects__in=request.user.favorites.all()
        ).distinct().order_by("-id")
    elif active_filter == "owners-of-participating-projects":
        users = User.objects.filter(
            owned_projects__participants=request.user
        ).distinct().order_by("-id")
    elif active_filter == "interested-in-my-projects":
        users = User.objects.filter(favorites__owner=request.user).distinct().order_by("-id")
    elif active_filter == "participants-of-my-projects":
        users = User.objects.filter(
            participated_projects__owner=request.user
        ).exclude(pk=request.user.pk)
        users = users.distinct().order_by("-id")
    context = {
        "participants": users,
        "page_obj": paginate(request, users),
        "active_filter": active_filter,
        "query_prefix": query_prefix(request),
    }
    return render(request, "users/participants.html", context)
