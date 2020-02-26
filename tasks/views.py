from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView, TemplateView
from django.views.generic.detail import DetailView
from tasks.models import TodoItem, Category, Priority
from django.core.cache import cache
from datetime import datetime



def index(request):

    from django.db.models import Count

    counts = Category.objects.annotate(total_tasks=Count(
        'todoitem')).order_by("-total_tasks")
    counts = {c.name: c.total_tasks for c in counts}

    p_counts = Priority.objects.annotate(total_tasks=Count('todoitem')).order_by("-total_tasks")
    p_counts = {p.name: p.total_tasks for p in p_counts}

    return render(request, "tasks/index.html", {"counts": counts, "p_counts": p_counts})


def filter_tasks(tags_by_task):
    return set(sum(tags_by_task, []))


def tasks_by_cat(request, cat_slug=None):
    u = request.user
    tasks = TodoItem.objects.filter(owner=u).all()

    cat = None
    if cat_slug:
        cat = get_object_or_404(Category, slug=cat_slug)
        tasks = tasks.filter(category__in=[cat])

    categories = []
    for t in tasks:
        for cat in t.category.all():
            if cat not in categories:
                categories.append(cat)

    return render(
        request,
        "tasks/list_by_cat.html",
        {"category": cat, "tasks": tasks, "categories": categories},
    )


class TaskListView(ListView):
    model = TodoItem
    context_object_name = "tasks"
    template_name = "tasks/list.html"

    def get_queryset(self):
        u = self.request.user
        qs = super().get_queryset()
        return qs.filter(owner=u)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user_tasks = self.get_queryset()
        if not user_tasks:
            context['empty'] = "Нет задач. Войдите в панель администратора и добавьте их."
            return context
        else:
            tags = []
            for t in user_tasks:
                tags.append(list(t.category.all()))

            categories = []
            for cat in t.category.all():
                if cat not in categories:
                    categories.append(cat)
            context["categories"] = categories

            return context


class TaskDetailsView(DetailView):
    model = TodoItem
    template_name = "tasks/details.html"

class ViewCacheTemplate(TemplateView):
    template_name = "tasks/cache.html"

    def get_context_data(self, **kwargs):
        context = super(ViewCacheTemplate, self).get_context_data(**kwargs)
        if cache.get('cached_datetime') == None:
            cache.set('cached_datetime', datetime.now())
            context['datetime'] = cache.get('cached_datetime')
            return context
        else:
            context['datetime'] = cache.get('cached_datetime')
            return context