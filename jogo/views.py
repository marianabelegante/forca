from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from .models import Tema, Palavra, Perfil
from .forms import FormularioRegistro, FormularioTema, FormularioPalavra

#HOME
class HomeView(TemplateView):
    template_name = 'jogo/home.html'


# REGISTRO
class RegistroView(CreateView):
    form_class = FormularioRegistro
    template_name = 'jogo/registro.html'
    success_url = reverse_lazy('login')


# LOGIN
class LoginUsuarioView(LoginView):
    template_name = 'jogo/login.html'


# LOGOUT
class LogoutUsuarioView(LogoutView):
    next_page = reverse_lazy('login')


# MIXIN: apenas professores
class SomenteProfessorMixin(UserPassesTestMixin):
    def test_func(self):
        return hasattr(self.request.user, 'perfil') and self.request.user.perfil.eh_professor

    def handle_no_permission(self):
        return redirect('login')


# CRUD TEMA (somente professores)
class TemaListView(LoginRequiredMixin, SomenteProfessorMixin, ListView):
    model = Tema
    template_name = 'jogo/tema_lista.html'
    context_object_name = 'temas'

    def get_queryset(self):
        return Tema.objects.filter(criado_por=self.request.user)


class TemaCreateView(LoginRequiredMixin, SomenteProfessorMixin, CreateView):
    model = Tema
    form_class = FormularioTema
    template_name = 'jogo/tema_formulario.html'
    success_url = reverse_lazy('temas')

    def form_valid(self, form):
        form.instance.criado_por = self.request.user
        return super().form_valid(form)


class TemaUpdateView(LoginRequiredMixin, SomenteProfessorMixin, UpdateView):
    model = Tema
    form_class = FormularioTema
    template_name = 'jogo/tema_formulario.html'
    success_url = reverse_lazy('temas')


class TemaDeleteView(LoginRequiredMixin, SomenteProfessorMixin, DeleteView):
    model = Tema
    template_name = 'jogo/tema_confirmar_exclusao.html'
    success_url = reverse_lazy('temas')


# CRUD PALAVRA (somente professores)
class PalavraListView(LoginRequiredMixin, SomenteProfessorMixin, ListView):
    model = Palavra
    template_name = 'jogo/palavra_lista.html'
    context_object_name = 'palavras'

    def get_queryset(self):
        return Palavra.objects.filter(tema__criado_por=self.request.user)


class PalavraCreateView(LoginRequiredMixin, SomenteProfessorMixin, CreateView):
    model = Palavra
    form_class = FormularioPalavra
    template_name = 'jogo/palavra_formulario.html'
    success_url = reverse_lazy('palavras')


class PalavraUpdateView(LoginRequiredMixin, SomenteProfessorMixin, UpdateView):
    model = Palavra
    form_class = FormularioPalavra
    template_name = 'jogo/palavra_formulario.html'
    success_url = reverse_lazy('palavras')


class PalavraDeleteView(LoginRequiredMixin, SomenteProfessorMixin, DeleteView):
    model = Palavra
    template_name = 'jogo/palavra_confirmar_exclusao.html'
    success_url = reverse_lazy('palavras')
