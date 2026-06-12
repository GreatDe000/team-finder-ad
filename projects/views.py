from http import HTTPStatus

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from team_finder.utils import paginate, query_prefix

from .forms import ProjectForm
from .models import Project

PROJECT_NOT_FOUND_MESSAGE = "Проект не найден"
FORBIDDEN_MESSAGE = "Недостаточно прав"


def get_project_for_json(pk):
    return Project.objects.filter(pk=pk).first()


def json_not_found(message=PROJECT_NOT_FOUND_MESSAGE):
    return JsonResponse(
        {"status": "error", "message": message},
        status=HTTPStatus.NOT_FOUND,
    )


def json_forbidden(message=FORBIDDEN_MESSAGE):
    return JsonResponse(
        {"status": "error", "message": message},
        status=HTTPStatus.FORBIDDEN,
    )


@require_GET
def project_list(request):
    projects = Project.objects.select_related("owner").prefetch_related("participants")
    projects = projects.order_by("-created_at")
    context = {
        "projects": projects,
        "page_obj": paginate(request, projects),
        "query_prefix": query_prefix(request),
    }
    return render(request, "projects/project_list.html", context)


@login_required
@require_GET
def favorite_projects(request):
    projects = request.user.favorites.select_related("owner").prefetch_related("participants")
    projects = projects.order_by("-created_at")
    return render(request, "projects/favorite_projects.html", {"projects": projects})


@require_GET
def project_detail(request, pk):
    project = get_object_or_404(
        Project.objects.select_related("owner").prefetch_related("participants"),
        pk=pk,
    )
    return render(request, "projects/project-details.html", {"project": project})


@login_required
@require_POST
def toggle_favorite(request, pk):
    project = get_project_for_json(pk)
    if project is None:
        return json_not_found()
    is_favorited = request.user.favorites.filter(pk=project.pk).exists()
    if is_favorited:
        request.user.favorites.remove(project)
    else:
        request.user.favorites.add(project)
    return JsonResponse({"status": "ok", "favorited": not is_favorited})


@login_required
@require_POST
def complete_project(request, pk):
    project = get_project_for_json(pk)
    if project is None:
        return json_not_found()
    if request.user != project.owner and not request.user.is_staff:
        return json_forbidden()
    if project.status == Project.OPEN:
        project.status = Project.CLOSED
        project.save(update_fields=("status",))
    return JsonResponse({"status": "ok", "project_status": project.status})


@login_required
@require_POST
def toggle_participate(request, pk):
    project = get_project_for_json(pk)
    if project is None:
        return json_not_found()
    if request.user == project.owner:
        return JsonResponse({"status": "ok", "participant": True})
    is_participant = project.participants.filter(pk=request.user.pk).exists()
    if is_participant:
        project.participants.remove(request.user)
    else:
        project.participants.add(request.user)
    return JsonResponse({"status": "ok", "participant": not is_participant})


@login_required
def create_project(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            project.participants.add(request.user)
            return redirect("projects:detail", pk=project.pk)
    else:
        form = ProjectForm()
    return render(request, "projects/create-project.html", {"form": form, "is_edit": False})


@login_required
def edit_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.user != project.owner and not request.user.is_staff:
        return json_forbidden()
    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect("projects:detail", pk=project.pk)
    else:
        form = ProjectForm(instance=project)
    return render(request, "projects/create-project.html", {"form": form, "is_edit": True})
