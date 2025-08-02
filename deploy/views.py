import hmac
import hashlib
import secrets
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from .models import GitProject, GitPushEvent
from .forms import GitProjectForm
from datetime import datetime
from django.db.models import Count
from django.utils.timezone import now, timedelta


def dashboard_view(request):
    # Dados para cartões
    total_projects = GitProject.objects.count()
    total_pushes = GitPushEvent.objects.count()
    latest_push = GitPushEvent.objects.order_by('-pushed_at').first()

    # Dados para gráfico de barras
    today = now().date()
    last_7_days = [today - timedelta(days=i) for i in range(6, -1, -1)]
    labels = [d.strftime('%d/%m') for d in last_7_days]
    data = [GitPushEvent.objects.filter(pushed_at__date=d).count() for d in last_7_days]

    # Dados para gráfico de pizza
    project_data = (
        GitPushEvent.objects.values('project__name')
        .annotate(total=Count('id'))
        .order_by('-total')
    )
    pie_labels = [item['project__name'] for item in project_data]
    pie_data = [item['total'] for item in project_data]

    # Dados para a tabela
    projects = GitProject.objects.all()

    return render(request, 'deploy/dashboard.html', {
        'total_projects': total_projects,
        'total_pushes': total_pushes,
        'latest_push': latest_push,
        'bar_labels': labels,
        'bar_data': data,
        'pie_labels': pie_labels,
        'pie_data': pie_data,
        'projects': projects,
    })


def check_updates(request):
    updates = GitProject.objects.filter(new_push=True).values('id', 'name')
    return JsonResponse({'updates': list(updates)})

def register_project(request):
    if request.method == 'POST':
        form = GitProjectForm(request.POST)
        if form.is_valid():
            project = form.save()
            webhook_path = reverse('webhook_git')
            webhook_url = request.build_absolute_uri(webhook_path)
            webhook_hint = f"{webhook_url}?secret={project.webhook_secret}"

            messages.success(request, f'Projeto "{project.name}" cadastrado! Configure o webhook no GitHub.')
            return render(request, 'deploy/register.html', {
                'form': GitProjectForm(), 
                'webhook_hint': webhook_hint
            })
    else:
        form = GitProjectForm()

    return render(request, 'deploy/register.html', {'form': form})

def monitor_projects(request):
    projects = GitProject.objects.all()
    return render(request, 'deploy/monitor.html', {'projects': projects})

@csrf_exempt
def webhook_git(request):
    if request.method == 'POST':
        signature = request.headers.get('X-Hub-Signature-256', '')
        if signature.startswith('sha256='):
            signature = signature[7:]
        raw_data = request.body
        try:
            payload = json.loads(raw_data)
        except json.JSONDecodeError:
            return HttpResponse(status=400)  # Payload inválido

        projects = GitProject.objects.all()
        for project in projects:
            computed_signature = hmac.new(
                key=project.webhook_secret.encode('utf-8'),
                msg=raw_data,
                digestmod=hashlib.sha256
            ).hexdigest()
            if hmac.compare_digest(computed_signature, signature):
                pusher = payload.get('pusher', {}).get('name', 'unknown')
                ref = payload.get('ref', 'unknown')
                commit_count = len(payload.get('commits', []))
                
                project.last_deploy = datetime.now()
                project.new_push = True
                project.save()

                GitPushEvent.objects.create(
                    project=project,
                    pusher=pusher,
                    ref=ref,
                    commit_count=commit_count,
                    raw_payload=payload
                )
                return HttpResponse(status=200)
        return HttpResponse(status=403)  # Assinatura inválida
    return HttpResponse(status=405)  # Método não permitido

def delete_project(request, pk):
    project = get_object_or_404(GitProject, pk=pk)
    if request.method == 'POST':
        project_name = project.name
        project.delete()
        messages.success(request, f'Projeto "{project_name}" excluído com sucesso!')
        return redirect('monitor_projects')
    return render(request, 'deploy/confirm_delete.html', {'project': project})

def mark_push_viewed(request, pk):
    project = get_object_or_404(GitProject, pk=pk)
    project.new_push = False
    project.save()
    messages.success(request, f'Push do projeto "{project.name}" marcado como visualizado.')
    return redirect('monitor_projects')