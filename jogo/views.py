from django.urls import reverse_lazy
import random
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, TemplateView, View
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect, render
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
            return reverse_lazy('temas')  # Professor vai pra lista de temas
        else:
            return reverse_lazy('selecionar_jogo')  # Aluno vai pra seleção do jogo


# LOGIN
class LoginUsuarioView(LoginView):
    template_name = 'jogo/login.html'

    def get_success_url(self):
        user = self.request.user
        if hasattr(user, 'perfil') and user.perfil.eh_professor:
            return reverse_lazy('temas')  # Professor vai pra lista de temas
        else:
            return reverse_lazy('selecionar_jogo')  # Aluno vai pra seleção do jogo


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
        # Lista só temas com pelo menos uma palavra
        context['temas'] = Tema.objects.filter(palavras__isnull=False).distinct()
        return context

class JogoDaForcaView(View):
    template_name = 'jogo/jogo_forca.html'

    def get(self, request, tema_id):
        # Pegando a palavra aleatória do tema
        palavras = Palavra.objects.filter(tema_id=tema_id)
        if not palavras.exists():
            return render(request, self.template_name, {'erro': 'Nenhuma palavra disponível para este tema.'})

        # Inicializar jogo se não existir na sessão ou tema mudou
        if 'jogo' not in request.session or request.session.get('tema_id') != tema_id:
            palavra = random.choice(list(palavras))
            request.session['jogo'] = {
                'palavra': palavra.texto.lower(),
                'acertos': [],
                'erros': 0,
                'max_erros': 6,
                'status': 'em_andamento'
            }
            request.session['tema_id'] = tema_id

        contexto = self._criar_contexto(request)
        return render(request, self.template_name, contexto)

    def post(self, request, tema_id):
        letra = request.POST.get('letra', '').lower()
        jogo = request.session.get('jogo')

        if not jogo or jogo['status'] != 'em_andamento':
            return redirect('selecionar_jogo')

        palavra = jogo['palavra']
        acertos = set(jogo['acertos'])
        erros = jogo['erros']
        max_erros = jogo['max_erros']

        if letra and letra.isalpha() and len(letra) == 1:
            if letra in palavra and letra not in acertos:
                acertos.add(letra)
            elif letra not in palavra:
                erros += 1

        # Atualizar o status do jogo
        if erros >= max_erros:
            jogo['status'] = 'perdeu'
        elif all(l in acertos for l in set(palavra)):
            jogo['status'] = 'ganhou'

        jogo['acertos'] = list(acertos)
        jogo['erros'] = erros

        request.session['jogo'] = jogo

        contexto = self._criar_contexto(request)
        return render(request, self.template_name, contexto)

    def _criar_contexto(self, request):
        jogo = request.session.get('jogo')
        palavra = jogo['palavra']
        acertos = set(jogo['acertos'])
        status = jogo['status']
        erros = jogo['erros']
        max_erros = jogo['max_erros']

        palavra_mostrada = ' '.join([l if l in acertos else '_' for l in palavra])

        return {
            'palavra_mostrada': palavra_mostrada,
            'palavra_original': palavra,
            'status': status,
            'erros': erros,
            'max_erros': max_erros,
            'letras_usadas': acertos,
        }