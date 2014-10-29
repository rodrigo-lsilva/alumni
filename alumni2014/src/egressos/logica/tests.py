# encoding: utf-8
"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from egressos.logica.models import Registro_Egresso, Dados_Atualizados, Usuario, Graduacao, Pos_Graduacao, Convite
from datetime import date
from django.contrib import auth
from django.test import Client
from django.utils import timezone
from django.contrib.auth.models import User
import egressos
import util


# class SimpleTest(TestCase):
#     def test_basic_addition(self):
#         """
#         Tests that 1 + 1 always equals 2.
#         """
#         print "abc"
#         self.assertEqual(1 + 1, 2)

nome="Fulano"
sexo="M"
email=""
nascimento=date(2013, 12, 5)
filiacao_ou_mae="MÃE"
pai="Pai"

def criaRegistro_Egresso():
    dadosAtuais=Dados_Atualizados.objects.create(nome_Atual=nome, data_atualizacao=timezone.now(), cidade="", pais="", onde_trabalha="", ocupacao="", setor_atuacao="")
    return Registro_Egresso.objects.create(nome=nome, sexo=sexo, nascimento=nascimento, filiacao_ou_mae=filiacao_ou_mae, naturalidade1="", naturalidade2="", endereco="", bairro="", municipio="", cep="", telefone="", email="", privacidade="privado", pagina_web="www.lll",dados_atuais=dadosAtuais)

def criaUsuario():
    return User.objects.create_superuser("usuario", "email@email.com", "123456")

def criaDadosAtualizados():
    return Dados_Atualizados.objects.create(nome_Atual="Nome", data_atualizacao=timezone.now(), cidade="", pais="", onde_trabalha="", ocupacao="", setor_atuacao="")
        
class RegistroEgressoTest(TestCase):
    nome="Fulano"
    sexo="M"
    email=""
    nascimento=date(2013, 12, 5)
    filiacao_ou_mae="MÃE"
    pai="Pai"
     
    def testCriacao(self):
        egresso=criaRegistro_Egresso()
        self.assertEqual(self.nome+" " + self.sexo + " " + self.nascimento.__str__() + " " + self.email , egresso.__unicode__(), "Erro na criação do objeto")
        self.assertTrue(egresso.id!=None, "Não há ID: %s" % egresso.id)
         
    def testEh_privado(self):
        egresso=criaRegistro_Egresso()
        egresso.privacidade="NAO"
        self.assertFalse(egresso.eh_privado(), "Privacidade: %s" %egresso.privacidade)
        egresso.privacidade=Registro_Egresso.PRIVADO
        egresso.save()
        self.assertTrue(egresso.eh_privado(), "Privacidade: %s" %egresso.privacidade)
         
    def testWebOK(self):
        egresso=criaRegistro_Egresso()
        self.assertFalse(egresso.web_ok(), "Página web: %s" %egresso.pagina_web)
        egresso.pagina_web="http://www.site.com"
        egresso.save()
        self.assertTrue(egresso.web_ok(), "Página web: %s" %egresso.pagina_web)
         
    def testEquals(self):
        egresso=criaRegistro_Egresso()
        egresso.nascimento=date(1990,01,01)
        egresso2=criaRegistro_Egresso()
        egresso2.nascimento=date(1990,01,01)
        egresso3=criaRegistro_Egresso()
        egresso3.nascimento=date(1990,04,01)
        egresso4=criaRegistro_Egresso()
        egresso4.nascimento=date(1990,04,05)
        egresso5=criaRegistro_Egresso()
        egresso5.nascimento=None
        egresso6=criaRegistro_Egresso()
        egresso6.nascimento=None
        self.assertTrue(egresso.equals(outro_egresso=egresso2), "%s" %egresso.equals(outro_egresso=egresso2) )
        self.assertTrue(egresso.equals(outro_egresso=egresso3), "%s" %egresso.equals(outro_egresso=egresso3) )
        self.assertFalse(egresso.equals(outro_egresso=egresso4), "%s" %egresso.equals(outro_egresso=egresso4) )
        self.assertTrue(egresso.equals(outro_egresso=egresso5), "%s" %egresso.equals(outro_egresso=egresso5) )
        self.assertTrue(egresso5.equals(outro_egresso=egresso6), "%s" %egresso5.equals(outro_egresso=egresso6) )
         
    def testMerge(self):
        egresso1=criaRegistro_Egresso()
        egresso1.nascimento=date(1990,01,01)
        egresso1.filiacao_ou_mae="mother oka-san"
        graduacao=Graduacao()
        graduacao.curso="curso"
        graduacao.matricula="matricula"
        graduacao.outras_matriculas=""
        graduacao.ingresso=""
        graduacao.forma_ingresso=""
        graduacao.evasao=""
        graduacao.situacao=""
        graduacao.save()
        egresso1.graduacao.add(graduacao)
        atua1=Dados_Atualizados()
        atua1.cidade="City"
        atua1.data_atualizacao=date(2000,01,01)
        egresso1.dados_atuais=atua1
        egresso1.bairro="bairro"
        egresso2=criaRegistro_Egresso()
        egresso2.nascimento=date(1992,03,01)
        egresso3=criaRegistro_Egresso()
        egresso3.nascimento=date(1990,01,01)
        egresso3.pai="father oto-san"
        egresso3.municipio="Cidade"
        egresso3.cep="123456"
        egresso3.email="email@email.com"
        posgraduacao=Pos_Graduacao()
        posgraduacao.programa="programa"
        posgraduacao.save()
        egresso3.pos_graduacao.add(posgraduacao)
        atua2=Dados_Atualizados()
        atua2.cidade="Condado"
        atua2.data_atualizacao=date(2010,01,02)
        egresso3.dados_atuais=atua2
        self.assertEqual(egresso1.merge(egresso2), None, "Erro egresso1: %s, egresso2: %s"  + egresso1.nascimento.__str__() + ", egresso2: " + egresso2.nascimento.__str__())
        egresso4=egresso1.merge(egresso3)
        self.assertEqual(egresso4.__unicode__(), egresso1.__unicode__(), "egresso 1 é diferente de egresso4")
        self.assertEqual(egresso4.filiacao_ou_mae, egresso1.filiacao_ou_mae,"mae")
        self.assertEqual(egresso4.pai, egresso3.pai, "pai")
        self.assertEqual(egresso4.bairro,egresso1.bairro,"bairro")
        self.assertEqual(egresso4.municipio, egresso3.municipio,"municipio")
        self.assertEqual(egresso4.cep,egresso3.cep,"cep")
        self.assertEqual(egresso4.dados_atuais.cidade, atua2.cidade, "cidade atualizada")
        self.assertEqual(egresso4.dados_atuais.data_atualizacao, atua2.data_atualizacao, "data de atualizacao")
        self.assertTrue(egresso4.graduacao.get(curso="curso").__unicode__() == egresso1.graduacao.get(curso="curso").__unicode__(), "graduacao")
        self.assertEqual(egresso4.pos_graduacao.get(programa="programa").__unicode__(), egresso3.pos_graduacao.get(programa="programa").__unicode__(), "pos_graduacao")
         


class ConviteTest(TestCase):
    
    def testCriacao(self):
        usuario=Usuario();
        usuario.usuario = criaUsuario();
        usuario.registro = criaRegistro_Egresso()
        convite = Convite();
        convite.de=usuario
        convite.para=usuario.registro
        convite.email="email@email.com"
        convite.id=1
        convite.chave=util.generate_key(convite.id)
        self.assertFalse(convite.is_ok(), "Verificação do status")
        convite.status=Convite.ok
        self.assertTrue(convite.is_ok(), "Verificação do status")

class Dados_AtualizadosTest(TestCase):
    
    def testCriacao(self):
        dados = criaDadosAtualizados()
        self.assertEqual(dados.nome_Atual, "Nome", "Verificação do Nome")
                       


class MainViewTest(TestCase):
     
    def setUp(self):
        self.client=Client()
         
    def testSimple(self):
        response=self.client.get("/")
        # O cliente será direcionado para /home, logo o código HTTP é 302 ("redirecionamento") 
        self.assertEqual(302, response.status_code, response.status_code)
        self.assertRedirects(response, expected_url="/home/")
        response=self.client.get("/home/")
        # Código 200: OK    
        self.assertEqual(200, response.status_code, response.status_code)
        
class LoginTest(TestCase):
     
    def setUp(self):
        self.client=Client(enforce_csrf_checks=False)
        user=User.objects.create_superuser(username='rodrigo', email='email@email.com', password='123456')
        user.save()
        dadosAtuais=criaDadosAtualizados()
        registro=Registro_Egresso.objects.create(nome="Nome", sexo="M", nascimento=date(2000,01,01), filiacao_ou_mae="mae", naturalidade1="", naturalidade2="", endereco="", bairro="", municipio="", cep="", telefone="", email="", privacidade="privado", pagina_web="www.lll",dados_atuais=dadosAtuais)
        registro.save()
        usuario=Usuario.objects.create(usuario=user, registro=registro) 
         
    def testSimple(self):
#         response=self.client.post("/login/", {"username": "rodrigo", "password": "123456"})
#         self.assertTrue(self.client.login(username='rodrigo', password='123456'), self.client.login(username='rodrigo', password='123456'))
        response=self.client.get("/home/")
        self.assertNotContains(response, text="Turmas", msg_prefix=response.content)
        self.assertTrue(self.client.login(username='rodrigo', password='123456'), "Not True")
        response=self.client.get("/home/")
        self.assertContains(response, text="Turmas", msg_prefix=response.content)
         
    def testConvites(self):
        response=self.client.get("/multiple_invites/")
        self.assertRedirects(response, "/login/?next=/multiple_invites/", status_code=302)
        response=self.client.post("/login/?next=/multiple_invites/", {"username": "rodrigo", "password": "123456"})
        self.assertRedirects(response, "/multiple_invites/", status_code=302)
        response=self.client.get("/multiple_invites/")
        self.assertContains(response, "Convite enviado com sucesso para os emails:")
        
         
#     def testLoginRedirect(self):
#         #Acesso a página de login
#         response=self.client.get("/login/")
#         self.assertContains(response, text="Login", status_code=200, msg_prefix="Não exibiu a página de login")
#         #Realização de login
#         response=self.client.post("/login/", {"username": "rodrigo", "password": "123456"})
#         
#         corrigir esse teste
#         corrigir esse teste
#         corrigir esse teste
#         corrigir esse teste
#         corrigir esse teste
# 
#         print "---------------------------"
#         print response
#         self.assertContains(response, text="e-mail", status_code=302, msg_prefix="erro", html=True)
#         response=self.client.get("/login/")
#         self.assertRedirects(response, expected_url="/", status_code=302, msg_prefix="Não ocorreu redirecionamento")
#         self.assertFalse(self.client.logout(), msg="Erro no logout")
        
        
        
#         self.assertTrue(self.client.login(username='rodrigo', password='123456'), "Not True")
#         response=self.client.get("/login/")
        
      

