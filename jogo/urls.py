from django.urls import path
from .views import (
    HomeView,
    RegistroView,
    LoginUsuarioView,
    LogoutUsuarioView,
    TemaListView,
    TemaCreateView,
    TemaUpdateView,
    TemaDeleteView,
    PalavraListView,
    PalavraCreateView,
    PalavraUpdateView,
    PalavraDeleteView
)

urlpatterns = [
    #Página inicial
    path('', HomeView.as_view(), name='home'),
    # Autenticação
    path('registro/', RegistroView.as_view(), name='registro'),
    path('login/', LoginUsuarioView.as_view(), name='login'),
    path('logout/', LogoutUsuarioView.as_view(), name='logout'),

    # Temas (somente professores)
    path('temas/', TemaListView.as_view(), name='temas'),
    path('temas/novo/', TemaCreateView.as_view(), name='novo_tema'),
    path('temas/<int:pk>/editar/', TemaUpdateView.as_view(), name='editar_tema'),
    path('temas/<int:pk>/excluir/', TemaDeleteView.as_view(), name='excluir_tema'),

    # Palavras (somente professores)
    path('palavras/', PalavraListView.as_view(), name='palavras'),
    path('palavras/nova/', PalavraCreateView.as_view(), name='nova_palavra'),
    path('palavras/<int:pk>/editar/', PalavraUpdateView.as_view(), name='editar_palavra'),
    path('palavras/<int:pk>/excluir/', PalavraDeleteView.as_view(), name='excluir_palavra'),
]
