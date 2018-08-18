from django.shortcuts import redirect
from django.views.generic import TemplateView, ListView, CreateView, FormView

from core import models
from core.manager.base import Manager


class Index(ListView):
    template_name = 'core/index.html'
    queryset = models.Node.objects.all()


class NodeCreate(CreateView):
    model = models.Node
    fields = '__all__'
    success_url = '/'

    def get_context_data(self, **kwargs):
        c = super().get_context_data(**kwargs)
        c['title'] = 'Create node'
        return c

    def form_valid(self, form):
        response = super().form_valid(form)

        manager = Manager.get_manager()
        manager.start(self.object)

        return response


class NodeStop(TemplateView):
    success_url = '/'
    template_name = 'core/node_stop.html'

    def get_object(self):
        return models.Node.objects.get(pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        c = super().get_context_data(**kwargs)
        c['title'] = 'Stop node'
        c['object'] = self.get_object()
        return c

    def post(self, request, *args, **kwargs):
        node = self.get_object()

        node.stop()

        return redirect(self.success_url)


class NodeDestroy(TemplateView):
    success_url = '/'
    template_name = 'core/node_destroy.html'

    def get_object(self):
        return models.Node.objects.get(pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        c = super().get_context_data(**kwargs)
        c['title'] = 'Destroy node'
        c['object'] = self.get_object()
        return c

    def post(self, request, *args, **kwargs):
        node = self.get_object()

        manager = Manager.get_manager()
        manager.stop(node)

        return redirect(self.success_url)
