from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.models import User
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

    def get_success_url(self):
        user = self.request.user
        if hasattr(user, 'perfil') and user.perfil.eh_professor:
            return reverse_lazy('temas')  # professor vai pra lista de temas
        else:
            return reverse_lazy('home')  # aluno vai pra home ou tela de jogo


# LOGIN
class LoginUsuarioView(LoginView):
    template_name = 'jogo/login.html'

    def get_success_url(self):
        user = self.request.user
        if hasattr(user, 'perfil') and user.perfil.eh_professor:
            return reverse_lazy('temas')  # professor vai pra lista de temas
        else:
            return reverse_lazy('home')  # aluno vai pra home ou tela de jogo


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
    template_name = 'jogo/temas.html'
    context_object_name = 'temas'

    def get_queryset(self):
        return Tema.objects.filter(criado_por=self.request.user)


class TemaCreateView(LoginRequiredMixin, SomenteProfessorMixin, CreateView):
    model = Tema
    form_class = FormularioTema
    template_name = 'jogo/tema_form.html'
    success_url = reverse_lazy('temas')

    def form_valid(self, form):
        form.instance.criado_por = self.request.user
        return super().form_valid(form)


class TemaUpdateView(LoginRequiredMixin, SomenteProfessorMixin, UpdateView):
    model = Tema
    form_class = FormularioTema
    template_name = 'jogo/tema_form.html'
    success_url = reverse_lazy('temas')


class TemaDeleteView(LoginRequiredMixin, SomenteProfessorMixin, DeleteView):
    model = Tema
    template_name = 'jogo/tema_confirm_delete.html'
    success_url = reverse_lazy('temas')


# CRUD PALAVRA (somente professores)
class PalavraListView(LoginRequiredMixin, SomenteProfessorMixin, ListView):
    model = Palavra
    template_name = 'jogo/palavras.html'
    context_object_name = 'palavras'

    def get_queryset(self):
        return Palavra.objects.filter(tema__criado_por=self.request.user)


class PalavraCreateView(LoginRequiredMixin, SomenteProfessorMixin, CreateView):
    model = Palavra
    form_class = FormularioPalavra
    template_name = 'jogo/palavra_form.html'
    success_url = reverse_lazy('palavras')


class PalavraUpdateView(LoginRequiredMixin, SomenteProfessorMixin, UpdateView):
    model = Palavra
    form_class = FormularioPalavra
    template_name = 'jogo/palavra_form.html'
    success_url = reverse_lazy('palavras')


class PalavraDeleteView(LoginRequiredMixin, SomenteProfessorMixin, DeleteView):
    model = Palavra
    template_name = 'jogo/palavra_confirm_delete.html'
    success_url = reverse_lazy('palavras')



class SelecaoJogoView(TemplateView):
    template_name = 'jogo/selecao_jogo.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        professor_id = self.request.GET.get('professor')
        tema_id = self.request.GET.get('tema')

        context['professores'] = User.objects.filter(temas_criados__isnull=False).distinct()
        context['temas'] = Tema.objects.all()

        palavras = Palavra.objects.all()

        if professor_id:
            palavras = palavras.filter(tema__criado_por_id=professor_id)
        if tema_id:
            palavras = palavras.filter(tema_id=tema_id)

        context['palavras'] = palavras
        context['professor_selecionado'] = int(professor_id) if professor_id else None
        context['tema_selecionado'] = int(tema_id) if tema_id else None
        return context
