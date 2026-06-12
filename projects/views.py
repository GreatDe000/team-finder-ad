import json

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseBadRequest, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from .forms import ProjectForm
from .models import Project, Skill


def query_prefix(request, *excluded):
    params = request.GET.copy()
    for key in ("page", *excluded):
        params.pop(key, None)
    encoded = params.urlencode()
    return f"{encoded}&" if encoded else ""


def paginate(request, queryset, per_page=12):
    return Paginator(queryset, per_page).get_page(request.GET.get("page"))


@require_GET
def project_list(request):
    projects = Project.objects.select_related("owner").prefetch_related("participants", "skills")
    active_skill = request.GET.get("skill")
    if active_skill:
        projects = projects.filter(skills__name=active_skill)
    projects = projects.order_by("-created_at")
    all_skills = Skill.objects.order_by("name").values_list("name", flat=True)
    context = {
        "projects": projects,
        "page_obj": paginate(request, projects),
        "all_skills": all_skills,
        "active_skill": active_skill,
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
        Project.objects.select_related("owner").prefetch_related("participants", "skills"),
        pk=pk,
    )
    return render(request, "projects/project-details.html", {"project": project})


@login_required
@require_POST
def toggle_favorite(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project in request.user.favorites.all():
        request.user.favorites.remove(project)
        favorited = False
    else:
        request.user.favorites.add(project)
        favorited = True
    return JsonResponse({"status": "ok", "favorited": favorited})


@login_required
@require_POST
def complete_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.user != project.owner and not request.user.is_staff:
        return HttpResponseForbidden()
    if project.status == Project.OPEN:
        project.status = Project.CLOSED
        project.save(update_fields=("status",))
    return JsonResponse({"status": "ok", "project_status": project.status})


@login_required
@require_POST
def toggle_participate(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.user == project.owner:
        return JsonResponse({"status": "ok", "participant": True})
    if request.user in project.participants.all():
        project.participants.remove(request.user)
        participant = False
    else:
        project.participants.add(request.user)
        participant = True
    return JsonResponse({"status": "ok", "participant": participant})


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
        return HttpResponseForbidden()
    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect("projects:detail", pk=project.pk)
    else:
        form = ProjectForm(instance=project)
    return render(request, "projects/create-project.html", {"form": form, "is_edit": True})


@require_GET
def skills_list(request):
    q = request.GET.get("q", "").strip()
    skills = Skill.objects.order_by("name")
    if q:
        skills = skills.filter(name__istartswith=q)
    data = list(skills.values("id", "name")[:10])
    return JsonResponse(data, safe=False)


@login_required
@require_POST
def add_project_skill(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.user != project.owner and not request.user.is_staff:
        return HttpResponseForbidden()
    payload = request_payload(request)
    skill = None
    created = False
    if payload.get("skill_id"):
        skill = get_object_or_404(Skill, pk=payload["skill_id"])
    elif payload.get("name"):
        name = payload["name"].strip()
        if not name:
            return HttpResponseBadRequest("Название навыка не указано")
        skill, created = Skill.objects.get_or_create(name=name)
    else:
        return HttpResponseBadRequest("Укажите skill_id или name")
    added = not project.skills.filter(pk=skill.pk).exists()
    if added:
        project.skills.add(skill)
    return JsonResponse(
        {
            "id": skill.pk,
            "name": skill.name,
            "skill_id": skill.pk,
            "created": created,
            "added": added,
        }
    )


@login_required
@require_POST
def remove_project_skill(request, pk, skill_id):
    project = get_object_or_404(Project, pk=pk)
    skill = get_object_or_404(Skill, pk=skill_id)
    if request.user != project.owner and not request.user.is_staff:
        return HttpResponseForbidden()
    if not project.skills.filter(pk=skill.pk).exists():
        return HttpResponseBadRequest("Навык не добавлен к проекту")
    project.skills.remove(skill)
    return JsonResponse({"status": "ok"})


def request_payload(request):
    if request.content_type == "application/json" and request.body:
        try:
            return json.loads(request.body.decode())
        except json.JSONDecodeError:
            return {}
    return request.POST
