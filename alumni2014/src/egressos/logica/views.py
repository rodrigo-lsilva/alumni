# -*- coding: utf-8 -*-
# Create your views here.

import PIL
import PIL.Image
import StringIO
import collections
from datetime import date
from django.contrib.auth import login, logout # funcao que salva o usuario na sessao
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm # Formulario de autenticacao de usuarios
from django.contrib.auth.forms import UserCreationForm # Formulario de criacao de usuarios
from django.contrib.auth.models import User
# from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.mail import send_mail
from django.core.validators import email_re
# from django.db.models.aggregates import Count
from django.http import HttpResponseRedirect, HttpResponse # Funcao para redirecionar o usuario
from django.shortcuts import render_to_response, render
from django.template.context import RequestContext
from django.template.loader import render_to_string
from django.utils import timezone

import MySQLdb as mdb
import psycopg2
from egressos import settings
from egressos.logica.models import Registro_Egresso, Usuario, Convite, Dados_Atualizados, Centro, UnidadeAcademica, Graduacao, Pos_Graduacao, Dominio, getID, setID, Estatisticas, getDominio
from egressos.logica.util import ano_inicial
import emailconf
import util

import matplotlib
matplotlib.use("AGG")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import pylab
from pylab import *


#import warnings

#Imports para geração de gráficos
#Imports para acesso ao banco de dados
#Imports do projeto
largura=8
altura=6
dpi=100

def graficoEgressosPorAno(request):
    """
    Cria um gráfico de linha com egressos por ano. 
    """
    estat=Estatisticas()
    estat.getDados(getDominio())
    plt.figure(figsize=(largura,altura), dpi=dpi, facecolor='white')
    #Graduação
    x1=[]
    y1=[]
    total1 = estat.total_egressos_graduacao_por_evasao
    for c in total1:
        if int(c['total']) > 0:
            y1.append(c['total'])
            #Desloca primeiro período para ano.0 e desloca o segundo período para ano.5
            x1.append(float(c['evasao'].replace(".2", ".5").replace(".1", ".0" )))
    
    l1, = plt.plot(x1,y1, linewidth=2)
    
    #Mestres
    x2=[]
    y2=[]
    total2 = estat.total_egressos_pos_graduacao_por_evasao
    for c in total2:
        if int(c['total']) > 0 :
            y2.append(c['mestres'])
            x2.append(float(c['evasao']))
    l2, = plt.plot(x2,y2, linewidth=2)
    
    x3=[]
    y3=[]
    for c in total2:
        if int(c['total']) > 0 :
            y3.append(c['doutores'])
            x3.append(float(c['evasao']))
    l3, = plt.plot(x3,y3, linewidth=2)
    
    plt.title(unicode("Gráfico de Egressos por Ano"), fontsize=12)
    plt.xlabel(unicode("Ano"), color='0.3')
    plt.ylabel("Total de egressos", color='0.3')
    plt.legend([l1, l2, l3], [unicode("Egressos da Graduação"), unicode("Egressos Mestrado"), unicode("Egressos Doutorado")], prop={'size':7})
#     plt.savefig("egressos/logica/static/graficoEgressosPorAno.png")
    
    canvas = plt.get_current_fig_manager().canvas
    canvas.draw()
    buffer = StringIO.StringIO()
    graphIMG = PIL.Image.frombytes("RGB", canvas.get_width_height(), canvas.tostring_rgb())
    graphIMG.save(buffer, "PNG")
    plt.close()
    return HttpResponse(buffer.getvalue(), mimetype="image/png")

def graficoEgressosVSRegistrados(request):
    """
    Gera um gráfico de barras que compara os egressos da graduação com os registros de egressos
    """
    estat=Estatisticas()
    estat.getDados(getDominio())
    ax = plt.subplot(111)
    ax.figure.canvas.draw()
    plt.figure(figsize=(largura,altura), dpi=dpi, facecolor='white')
    #Graduação
    x1=[]
    y1=[]
    total1 = estat.total_egressos_graduacao_por_evasao
    for c in total1:
        if int(c['total']) > 0:
            y1.append(c['total'])
            x1.append(float(c['evasao'].replace(".2", ".5").replace(".1", ".0" )))
            
    x2=[]
    y2=[]
    total2 = estat.total_usuarios_registrados_graduacao_por_evasao
    for c in total2:
        if int(c['total']) > 0:
            y2.append(c['total'])
            x2.append(float(c['evasao'].replace(".2", ".5").replace(".1", ".0" )))
            
            
    ax = plt.subplot(111)
    b1 = ax.bar(x1, y1, width=0.4, label=unicode("Egressos - Graduação"), align="center")
    b2 = ax.bar(x2, y2, color="red", width=0.4, label=unicode("Cadastrados - Graduação"), align="center")
    ax.legend(prop={'size':7})
    plt.title(unicode("Gráfico de Egressos e Usuários Cadastrados na Graduação por Período"), fontsize=11)
    plt.xlabel("Ano de egresso", color='0.3')
    plt.ylabel("Total", color='0.3')
#     plt.savefig("egressos/logica/static/graficoEgressosVSRegistrados.png")
    
    canvas = plt.get_current_fig_manager().canvas
    canvas.draw()
    buffer = StringIO.StringIO()
    graphIMG = PIL.Image.frombytes("RGB", canvas.get_width_height(), canvas.tostring_rgb())
    graphIMG.save(buffer, "PNG")
    plt.close()
    return HttpResponse(buffer.getvalue(), mimetype="image/png")

def graficoEgressosVSRegistrados2(request):
    """
    Gera um gráfico de barras que compara os egressos da pós-graduação com os registros de egressos
    """
    estat=Estatisticas()
    estat.getDados(getDominio())
    ax = plt.subplot(111)
    ax.figure.canvas.draw()
    plt.figure(figsize=(largura,altura), dpi=dpi, facecolor='white')
            
    #Pós-Graduação
    x3=[]
    y3=[]
    total3 = estat.total_egressos_pos_graduacao_por_evasao
    for c in total3:
        if int(c['total']) > 0:
            y3.append(c['total'])
            #Deslocamento da posição em 0.5 para não sobrepor as barras da graduação
            x3.append(float(c['evasao']) + 0.5)
    
    x4=[]
    y4=[]
    total4 = estat.total_usuarios_registrados_pos_graduacao_por_evasao
    for c in total4:
        if int(c['total']) > 0:
            y4.append(c['total'])
            #Deslocamento da posição em 0.5 para não sobrepor as barras da graduação
            x4.append(float(c['evasao']) + 0.5)            
    
    b3 = ax.bar(x3, y3, color="green", width=0.4, label=unicode("Egressos - Pós-Graduação"), align="center")
    b4 = ax.bar(x4, y4, color="darkslategray", width=0.4, label=unicode("Cadastrados - Pós-Graduação"), align="center")
#     ax.legend(prop={'size':7})
    plt.title(unicode("Gráfico de Egressos e Usuários Cadastrados na Pós-Graduação por Ano"), fontsize=11)
    plt.xlabel("Ano de egresso", color='0.3')
    plt.ylabel("Total", color='0.3')
#     plt.savefig("egressos/logica/static/graficoEgressosVSRegistrados2.png")

    canvas = plt.get_current_fig_manager().canvas
    canvas.draw()
    buffer = StringIO.StringIO()
    graphIMG = PIL.Image.frombytes("RGB", canvas.get_width_height(), canvas.tostring_rgb())
    graphIMG.save(buffer, "PNG")
    plt.close()
    return HttpResponse(buffer.getvalue(), mimetype="image/png")




def estatisticas(request):
    """Exibe a página contendo os gráficos estatísticos"""
#     estat = Estatisticas()
    dominio = getDominio()
#     estat.getDados(dominio)
#     try:
#         graficoEgressosPorAno(estat)
#         graficoEgressosVSRegistrados(estat)
#         graficoEgressosVSRegistrados2(estat)
#     except:
#         print "Erro nas Estatísticas:", sys.exc_info()
    nome_dominio = dominio.unidadeAcademica.nome 
    if dominio.isCentro:
        nome_dominio = dominio.centro.nome
    return render_to_response("estatisticas.html", {"user":request.user, "pagina": "estatisticas", "nome_dominio": nome_dominio}, context_instance=RequestContext(request))

                           
def getRotulos(query):
    """
    Tenta recuperar os rótulos das colunas em uma consulta SQL
    """
    try:
        q=query.upper()
        #Se os nomes dos campos não forem informados, não é possível determiná-los.
        if q.count("*") > 0:
            return None
        else:
            inicio=q.index("SELECT")+6
            terminio=q.index("FROM")
            return q[inicio:terminio].rstrip().lstrip().split(",")
    except:
        return None

@login_required(login_url="/login/")
def executeQuery(request):
    """
    Permite ao administrador executar consultas no banco de dados. Operações de alteração do banco de dados não são aceitas.
    """
    #Verifica se o usuário tem permissão para realizar consultas
    if request.user.usuario.isAdministrador():
        # Verifica se ocorreu uma requisição utilizando o método POST
        if request.POST:
            query = request.POST['query']
            query=query.replace("<", "&lt;").replace(">", "&gt;").replace(";", "")
            #Verifica se a consulta realiza alguma operação inválida, como insert e delete
            if validQuery(query):
                default = settings.DATABASES['default']
                consulta = []
                #Execute a consulta no banco de dados
                consulta=[]
                rotulos=getRotulos(query)
                try:
                    if default['ENGINE'].count('mysql'):
                        consulta = executaConsultaMYSQL(default, query)
                    elif default['ENGINE'].count('postgres'):
                        consulta = executaConsultaPostgres(default, query)
                        
                except:
                    print "Consulta inválida:", query
                    
                return render_to_response("consultas.html", {"user":request.user, "message": "", "consulta": consulta, "rotulos":rotulos, "query":query, "pagina": "administracao"}, context_instance=RequestContext(request))    
            else:
                return render_to_response("consultas.html", {"user":request.user, "message": "Consulta inválida: não são permitidos termos que alterem o conteúdo do banco de dados, como INSERT, UPDATE, DELETE, DROP, CREATE E \";\"", "pagina": "administracao"}, context_instance=RequestContext(request))
        else:
            return render_to_response("consultas.html", {"user":request.user, "message": "", "pagina": "administracao"}, context_instance=RequestContext(request))
    else:
        return render_to_response("consultas.html", {"user":request.user, "message": "Usuário não autorizado a realizar consultas", "pagina": "administracao"}, context_instance=RequestContext(request))
        
def validQuery(query):
    """
    Verifica se uma consulta possui alguma operação inválida
    """
    q=query.upper()
    count = 0
    count += q.count('INSERT') + q.count('DELETE') + q.count('UPDATE') + q.count('DROP') + q.count('CREATE')
    return count == 0
    
def executaConsultaMYSQL(database, query):
    """
    Executa uma consulta em uma banco de dados MYSQL.
    @return: List contendo os resultados da consulta.
    """
    con = mdb.connect(database['HOST'], database['USER'], database['PASSWORD'], database['NAME'], charset='utf8')
    cursor = con.cursor()
    print "Consulta: ", query
    cursor.execute(query)
    return cursor.fetchall()

def executaConsultaPostgres(database, query):
    """
    Executa uma consulta em uma banco de dados Postgres.
    @return: List contendo os resultados da consulta.
    """
    connection = "host='" + database['HOST'] + "' dbname='" +  database['NAME'] + "' user='" + database['USER'] + "' password='" + database['PASSWORD'] + "'"
    conn = psycopg2.connect(connection)
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

@login_required(login_url="/login/")
def personalizacao(request):
    """
    View que possibilita a personalização do texto da página inicial
    """
    dominio = getDominio()
    if request.user.usuario.isAdministradorDominio(dominio):
        message = ""
        if request.POST:
            texto = request.POST["textoPaginaInicial"]
            dominio.textoPaginaInicial = texto
            dominio.save()
            message="Alterações realizadas com sucesso"
            try:
                data = request.FILES['css']
                path = default_storage.save("egressos/logica/static/logica/default.css2", ContentFile(data.read()))
            except:
                print sys.exc_info()[0]
                
            try:
                data = request.FILES['favicon']
                path = default_storage.save("egressos/logica/static/logica/images/favicon.ico", ContentFile(data.read()))
            except:
                print sys.exc_info()[0]
                
            try:
                data = request.FILES['logotipo']
                path = default_storage.save("egressos/logica/static/logica/default.css2", ContentFile(data.read()))
            except:
                print sys.exc_info()[0]
                
        return render_to_response("personalizacao.html", { "pagina": "administracao", "variaveis": dominio.getVariaveisExplicacao(), "marcacoes": dominio.getBBCodeExplicacacao(), "dominio":dominio, "message":message}, context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect("/home/")

@login_required(login_url="/login/")
def administracao(request):
    dominio = getDominio()
    if request.user.usuario.isAdministradorDominio(dominio):
        return render_to_response("administracao.html", { "pagina": "administracao"}, context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect("/home/")
    
@login_required(login_url="/login/")
def changepasswd(request):
    """Altera a senha de um usuário"""
    if request.POST:
        if request.POST["atual"] == None or request.POST["atual"] == "":
            return render_to_response("changepasswd.html", {"user":request.user, "m3":"*Senha atual não foi digitada", "pagina": "edit"}, context_instance=RequestContext(request))
        user = User.objects.get(username=request.user)
        if not user.check_password(request.POST["atual"]):
            return render_to_response("changepasswd.html", {"user":request.user, "m3":"*Senha atual incorreta", "pagina": "edit"}, context_instance=RequestContext(request))
        if request.POST["password"] != request.POST["password2"]:
            return render_to_response("changepasswd.html", {"user":request.user, "m3":"*Senha diferente", "pagina": "edit"}, context_instance=RequestContext(request))
        request.user.set_password(request.POST["password"])
        request.user.save()
        return HttpResponseRedirect("/home/")
    #return render_to_response("changepasswd.html", {"user":request.user})
    return render_to_response("changepasswd.html", {"pagina": "edit"}, context_instance=RequestContext(request))

def emailsave(request):
    email = request.GET.get('email')
    senha = request.GET.get('senha')    
    assunto = request.GET.get("assunto")
    corpo = request.GET.get("corpo")    
    var = open("/egressos/logica/emailconf.py","w")
    var.write("# -*- coding: utf-8 -*-")
    var.write("\n")
    var.write("email = '"+email+"'\n")
    var.write("senha = '"+senha+"'\n")
    var.write("assunto = '"+assunto+"'\n")
    var.write("corpo = '"+corpo+"'")
    var.close()
    return render_to_response("email_save.html", {"user":request.user })

def email(request):
#     import emailconf
    return render_to_response("email.html", {"user":request.user, "email":emailconf.email, "senha":emailconf.senha,"assunto":emailconf.assunto,"corpo":emailconf.corpo })

def main(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect("/home/")
    if request.user.is_superuser:
        return HttpResponseRedirect("/email/")
    return HttpResponseRedirect("/profile/"+str(request.user.usuario.id))

@login_required(login_url="/login/")
def myclass(request):
    
    # Dicionários de curso:[egressos_mesmo_ingresso, egressos_mesma_conclusao]
    turmas={}
    
    #itera sobre todos os cursos de graduação realizados pelo usuário e recupera os egressos do mesmo curso e com data de ingresso ou evasoes iguais ao do usuário
    try:
        for g in request.user.usuario.registro.graduacao.all():
            ingressos = Registro_Egresso.objects.filter(graduacao__curso=g.curso).filter(graduacao__ingresso=g.ingresso).order_by("nome").distinct()
            curso_ingresso = []
            for i in ingressos:
                tmp = [i, g.curso]
                curso_ingresso.append(tmp)
                
            evasoes = Registro_Egresso.objects.filter(graduacao__curso=g.curso).filter(graduacao__evasao=g.evasao).order_by("nome").distinct()
            curso_conclusao = []
            for e in evasoes:
                tmp = [e, g.curso]
                curso_conclusao.append(tmp)
        
            turmas.update({g:[curso_ingresso, curso_conclusao]})
    except: 
        print "Unexpected error:", sys.exc_info()[0]
    
    #Iteração similar a realizada na pós-graduacao, porém ingresso e evasao são datas e a comparação é realizada por ano.
    try:
        for pg in request.user.usuario.registro.pos_graduacao.all():
            ingressos = Registro_Egresso.objects.filter(pos_graduacao__programa=pg.programa).filter(pos_graduacao__ingresso__year=pg.ingresso.year).order_by("nome").distinct()
            programa_ingresso = []
            for i in ingressos:
                tmp = [i, pg.programa]
                programa_ingresso.append(tmp)
                
            evasoes = Registro_Egresso.objects.filter(pos_graduacao__programa=pg.programa).filter(pos_graduacao__evasao__year=pg.evasao.year).order_by("nome").distinct()
            programa_conclusao = []
            for e in evasoes:
                tmp = [e, pg.programa]
                programa_conclusao.append(tmp)
                
            turmas.update({pg:[programa_ingresso, programa_conclusao]})
    except:
        print "- Unexpected error:", sys.exc_info()[0]
        
#     turmas = collections.OrderedDict(sorted(turmas.items()))
    return render_to_response("my_class.html", {"user":request.user, "turmas":turmas, "pagina": "class" })

def exist(request, egresso_id):
    try:
        egresso = Usuario.objects.get(id=egresso_id)
    except:
        return HttpResponseRedirect("/profileNotFound/"+egresso_id+"/")
    return render_to_response("exist.html", {"user":request.user, "egresso":egresso })

def profile(request, egresso_id):
    try:
        egresso = Usuario.objects.get(id=egresso_id)
    except:
        return HttpResponseRedirect("/profileNotFound/"+egresso_id+"/")
    return render_to_response("profile.html", {"user":request.user, "usuario":egresso })

@login_required(login_url="/login/")    
def invites(request):
    convites = Convite.objects.filter(de=request.user.usuario)
    return render_to_response("invites.html", {"user":request.user, "convites":convites, "pagina": "invites" })  

"""
Exibe o assistente de cadastro
"""
def wizard(request, registro_id, key):
    print key
    registro = Registro_Egresso.objects.get(id=registro_id)
    if request.POST:
        dia = int(request.POST["dia"])
        mes = int(request.POST["mes"])
        ano = int(request.POST["ano"])
        if registro.nascimento != None and len(registro.nascimento.split(" ")[0].split("/")) == 3:
            data = registro.nascimento.split(" ")[0].split("/")
            dia_r = int(data[0])
            mes_r = int(data[1])
            ano_r = int(data[2][2:])
            print dia, mes, ano
            print dia_r, mes_r, ano_r
            if dia != dia_r or mes != mes_r or ano != ano_r:
                return render_to_response("real_wizard.html", {"user":request.user, "registro":registro, "key":key, "message": "A data difere do nosso registro" }, context_instance=RequestContext(request))
            else:
                convite = Convite.objects.get(chave__contains=key)
                convite.para = registro
                convite.save()
                return HttpResponseRedirect("/invite/"+key+"/")
        else:
            return render_to_response("real_wizard.html", {"user":request.user, "registro":registro, "key":key, "message":"Sua data de nascimento não consta nos nossos registros, entre em contato solicitando um convite através do e-mail: alumni@dsc.ufcg.edu.br" }, context_instance=RequestContext(request))
    return render_to_response("real_wizard.html", {"user":request.user, "registro":registro, "key":key }, context_instance=RequestContext(request))


@login_required(login_url="/login/")
def profileNotFound(request, registro_id):
    return render_to_response("profileNotFound.html", {"user":request.user, "message": "Perfil com id " + str(registro_id) + " não foi localizado."})

@login_required(login_url="/login/")
def userinvite(request, registro_id):
    """
        Envia um convite para o usuário com Registro_egresso.id = registro_id. Caso o usuário já esteja registro, encaminha para a página do profile
    """
    message = ""
    try:
        registro = Registro_Egresso.objects.get(id=registro_id)
        if registro.usuario:
            return HttpResponseRedirect("/profile/"+str(registro.usuario.id)+"/")
#     except ObjectDoesNotExist:
#             return HttpResponseRedirect("/profileNotFound/"+registro_id+"/")
    except:
        pass
      
    if request.GET:
        print "enviou o email"
        email = request.GET.get("email")
        
        if not email_re.match(email):
            message = "email invalido"
        else:
#             warnings.filterwarnings("ignore", "Field 'id' doesn't have a default value")
            u_id = request.user.usuario.id
            r_id = registro_id
            email = request.GET.get("email")
            u = Usuario.objects.get(id=u_id)
            r = Registro_Egresso.objects.get(id=r_id)
            
            convites = Convite.objects.filter(de=u)
            convites = convites.filter(para=r)
            convites = convites.filter(email=email)
            if len(convites) == 0:
                c = Convite()
                c.de = u
                c.para = r
                c.email = email
                c.status = "pendente"
                print c
                c.save()
                c.chave = util.generate_key(c.id)
                c.save()
                context = {"link":('http://alumni.dsc.ufcg.edu.br/invite/'+c.chave)}
                send_mail(emailconf.assunto.replace("{{ de }}", request.user.usuario.registro.nome), render_to_string('template_email.html', context), emailconf.email, [c.email], fail_silently=False)
                message = "Convite enviado com sucesso para: "
                clean_emails = [email]
                return render_to_response("sent.html", {"user":request.user, "message":message, "clean":clean_emails })
            else:
                message = "Voce ja enviou convite para esse e-mail"
        
    return render(request, "user_invite.html", {"user":request.user, "registro":registro, "message":message })

# def get_estatisticas():
# #     return None
#     maior = None
#     n = 0
#     menor = None
#     n2 = 1000000
#     for periodo in range(ano_inicial, util.getProximoAno()):
#         #Verificação do primeiro período
#         registros = Registro_Egresso.objects.filter(evasao__contains=str(periodo)+".1")
#         #Determina o período com maior número de egressos
#         if maior == None or len(registros) > n:
#             maior = str(periodo)+".1"
#             n = len(registros)
#         
#         #Determina o periodo com o menor número de egressos, desde que o valor seja maior que zero 
#         if (menor == None or len(registros) < n2) and len(registros) != 0:
#             menor = str(periodo)+".1"
#             n2 = len(registros)
#         
#         #Verificação do segundo período
#         registros = Registro_Egresso.objects.filter(evasao__contains=str(periodo)+".2")
#              
#         if maior == None or len(registros) > n:
#             maior = str(periodo)+".2"
#             n = len(registros)
#              
#         if (menor == None or len(registros) < n2) and len(registros) != 0    :
#             menor = str(periodo)+".2"
#             n2 = len(registros)
#      
#     Estatisticas = [
#         len(Registro_Egresso.objects.all()),
#         len(Registro_Egresso.objects.filter(curso__contains="PROCESSAMENTO")),
#         len(Registro_Egresso.objects.filter(curso__contains="CIENCIA")),
#         808,
#         (len(Registro_Egresso.objects.all()) - 808),
#         len(Usuario.objects.all()),
#         len(Registro_Egresso.objects.all()) - len(Usuario.objects.all()),
#       #n,
#       #menor,
#       #n2,
#       #len(Registro_Egresso.objects.all()),
#       #len(Registro_Egresso.objects.filter(sexo__contains="F")),
#       #len(Registro_Egresso.objects.filter(sexo__contains="M")),
#       #len(Usuario.objects.all()),
#       #9,10,11,12,13
#       ]
#     return Estatisticas


def home(request):
    """
    Exibe a tela inicial do sistema. Caso seja a primeira execução do sistema, exibe uma tela de configuração
    """
#     Caso o sistema não esteja configurado, exibe uma tela de configuração.
    try:
        id = getID()
    except:
        return render_to_response("config.html", {"pagina": "home"},context_instance=RequestContext(request))
    dominio=getDominio()
    return render_to_response("home.html", {"user":request.user, "texto":dominio.textoFormatado(), "pagina": "home" })


def config(request):
    """
    Configura o domínio atual
    """
    print "config"
    if request.POST:
        id = str(request.POST["id"])
        print id
        if len(id) < 1:
            return render_to_response("config.html", {"message": "ID inválido", "id": id}, context_instance=RequestContext(request))
        else:
            setID(id)
            return HttpResponseRedirect("/home/")
            
        

def registrado(request, convite):
    convite.status = convite.ok
    convite.save()
    username = request.GET.get("username")
    senha = request.GET.get("password")

    django_user = User.objects.create_user(username, password=senha)
    django_user.save()

    u = Usuario()
    registro = convite.para
    dados_atuais = registro.dados_atuais
    dados_atuais.nome_atual = request.GET.get('nome_atual')
    dados_atuais.cidade = request.GET.get('cidade')
    dados_atuais.pais = request.GET.get('pais')
    dados_atuais.onde_trabalha = request.GET.get('onde_trabalha')
    dados_atuais.ocupacao = request.GET.get('ocupacao')
    dados_atuais.setor_atuacao = request.GET.get('setor_atucao')
    dados_atuais.privacidade = request.GET.get('privacidade')
    registro.pagina_web = request.GET.get('pagina_web')
    dados_atuais.save()
    registro.save()
    
    u.usuario = django_user
    u.registro = convite.para
    u.save()

def invite(request, key):
    periodos = []
    registros = []
    for ano in range(ano_inicial, util.getProximoAno()):
        periodos.append(str(ano)+".1")
        periodos.append(str(ano)+".2")
    if request.user.is_authenticated():
        logout(request)
    convite = Convite.objects.get(chave__contains=key)
    if convite.status == convite.ok:
        return render_to_response("used.html", {"user":request.user})
    if convite.de.registro == convite.para:
        # convite para email
        if request.GET:
            codigos = ['\xc3\x83', '\xc3\xa3', '\xc3\x95', '\xc3\xb5', '\xc3\x81', '\xc3\xa1', '\xc3\x89', '\xc3\xa9', '\xc3\x8d', '\xc3\xad', '\xc3\x93', '\xc3\xb3', '\xc3\x9a', '\xc3\xba', '\xc3\x82', '\xc3\xa2', '\xc3\x8a', '\xc3\xaa', '\xc3\x8e', '\xc3\xae', '\xc3\x94', '\xc3\xb4', '\xc3\x9b', '\xc3\xbb']
            traducao = "AaOoAaEeIiOoUuAaEeIiOoUu"

        boolean = request.GET.get('boolean', False)
        termos = request.GET.get("termos").rstrip().lstrip()
        safe_termos = termos.encode('utf-8', 'ignore')
        ingresso = request.GET.get("ingresso")
        conclusao = request.GET.get("conclusao")
        termos = termos.split(" ")
        safe_termos = safe_termos.split(" ")
        for i in range(len(safe_termos)):
            for j in range(len(codigos)):
                safe_termos[i] = safe_termos[i].replace(codigos[j],traducao[j])

        termos = safe_termos         
        registros = Registro_Egresso.objects.filter(nome__contains=str(termos[0]).upper())
        for i in range(len(termos)):
            temp = Registro_Egresso.objects.filter(nome__contains=str(termos[i]).upper())
            
        if boolean == "and":
            registros = temp & registros
        else:
            registros = temp | registros
            
        if ingresso != "nenhum":
            registros = registros.filter(ingresso__contains=str(ingresso))
            
        if conclusao != "nenhum":
            registros = registros.filter(evasao__contains=str(conclusao))
            
        registros = registros.order_by("nome")
        return render_to_response("wizard.html", {"user":request.user, "convite":convite, "registros":registros, "periodos":periodos })
#     return render_to_response("wizard.html", {"user":request.user, "convite":convite, "registros":registros, "periodos":periodos })
            
    else:
        # convite direto
        if request.GET:
            if request.GET.get("nome_atual") == "":
                return render_to_response("invite.html", {"user":request.user, "convite":convite, "m1":"*Nome requerido" })
            
            email = request.GET.get("username")
            if not email_re.match(email):
                return render_to_response("invite.html", {"user":request.user, "convite":convite, "m2":"*E-mail invalido" })
            
            if len(User.objects.filter(username=email)) != 0:
                return render_to_response("invite.html", {"user":request.user, "convite":convite, "m2":"*E-mail '"+email+"' ja cadastrado" })
            
            if request.GET.get("password") == None or request.GET.get("password") == "":
                return render_to_response("invite.html", {"user":request.user,"convite":convite,  "m3":"*Senha não foi digitada" })
            
            if request.GET.get("password") != request.GET.get("password2"):
                return render_to_response("invite.html", {"user":request.user, "convite":convite, "m3":"*Senha diferente" })
            
            registrado(request, convite)
            return HttpResponseRedirect("/login/")
    return render_to_response("invite.html", {"user":request.user, "convite":convite })


def listPeriodos():
    """
        Cria uma lista com todos os períodos possíveis para busca.
    """
    periodos = []
    for ano in range(ano_inicial, util.getProximoAno()):
        periodos.append(str(ano)+".1")
        periodos.append(str(ano)+".2")
    return periodos

def textClear(texto):
    """
        Realiza o processamento de um texto, removendo caracteres com problemas de encoding e espaços em branco no início ou fim do texto.
        @return: List contendo as palavras do texto. 
    """
    codigos = ['\xc3\x83', '\xc3\xa3', '\xc3\x95', '\xc3\xb5', '\xc3\x81', '\xc3\xa1', '\xc3\x89', '\xc3\xa9', '\xc3\x8d', '\xc3\xad', '\xc3\x93', '\xc3\xb3', '\xc3\x9a', '\xc3\xba', '\xc3\x82', '\xc3\xa2', '\xc3\x8a', '\xc3\xaa', '\xc3\x8e', '\xc3\xae', '\xc3\x94', '\xc3\xb4', '\xc3\x9b', '\xc3\xbb']
    traducao = "AaOoAaEeIiOoUuAaEeIiOoUu"
    text = texto.rstrip().lstrip()
    text = text.encode('utf-8', 'ignore')
    for j in range(len(codigos)):
        text = text.replace(codigos[j],traducao[j])
    return text.split()
    

def search(request):
    """
    Realiza consultas por egressos
    """
    periodos = listPeriodos()
    registros = []
    safe_termos = []
    ingresso = "nenhum"
    conclusao = "nenhum"
    termos = ""
    
    dominio = getDominio()
    
    if request.POST:
        boolean = request.POST['boolean']
        termos = request.POST["termos"]
        safe_termos = textClear(termos)
        ingresso = request.POST["ingresso"]
        conclusao = request.POST["conclusao"]
        if len(safe_termos) > 0:
            registros = Registro_Egresso.objects.filter(nome__icontains=str(safe_termos[0]).upper())
        
            for i in safe_termos:
                print i
                temp = Registro_Egresso.objects.filter(nome__icontains=str(i.upper()))
                if boolean == "and":
                    registros = temp & registros
                else:
                    registros = temp | registros
            
            #Filtra o período de ingresso
            if ingresso != "nenhum":
                registros = registros.filter(graduacao__ingresso=str(ingresso))
                #Compara apenas o ano
                tmp = ingresso[:4]
                registros = registros | registros.filter(pos_graduacao__ingresso__contains=str(tmp))
            
            #Filtra o período de evasao
            if conclusao != "nenhum":
                registros = registros | registros.filter(graduacao__evasao=str(conclusao))
                #Compara apenas o ano
                tmp = conclusao[:4]
                registros = registros | registros.filter(pos_graduacao__evasao__contains=str(tmp))
            
                registros = registros.distinct().order_by("nome")
            if dominio.isCentro:
                registros = registros.filter(graduacao__unidadeAcademica__centro__id=dominio.centro.id)
            else:
                registros = registros.filter(graduacao__unidadeAcademica__centro__id=dominio.unidadeAcademica.id)
            registros = registros.order_by("nome").distinct()
    return render_to_response("search.html", {"user":request.user, "periodos":periodos, "registros":registros, "ingresso": ingresso, "conclusao":conclusao, "termos": termos,  "pagina": "search"}, context_instance=RequestContext(request))        

@login_required(login_url="/login/")
def multipleinvite(request):
    """
    Envia convite para egressos
    """
    e = ""
    clean_emails = []
    message = ""
    if not request.user.is_authenticated():
        return HttpResponseRedirect("/login/")
        print "not loged in"
    
    #Lê a lista de e-mail, caso exista
    emails = []
    if request.POST:
        emails = request.POST["emails"].split(",")
        for i in range(len(emails)):
            emails[i] = emails[i].rstrip().lstrip()
            if not email_re.match(emails[i]):
                message = emails[i]+": email invalido"
                break
            
    #Caso um usuário logado que não possua um registro, o mesmo será criado
    try:
        usuario = request.user.usuario
    except:
        # User não tem usuário e registro associados
        usuario = createRegistro(request.user)
#         return render_to_response("multiple_invite.html", {"user":request.user, "message":message, "clean":clean_emails, "emails":e }, context_instance=RequestContext(request))

    #Caso existam endereços informados, envia e-mail para os mesmos.
    if len(emails) > 0:
        message = "Convite enviado com sucesso para os emails:"
        for e in emails:
            c = Convite()
            c.de = usuario
            # quando eh anonimo ele manda convite pra ele mesmo
            c.para = c.de.registro
            c.email = e
            c.status = c.pendente
            c.save()
            c.chave = util.generate_key(c.id)
            c.save()
            context = {"link":('http://alumni.dsc.ufcg.edu.br/invite/'+c.chave)}
            send_mail(emailconf.assunto.replace("{{ de }}", request.user.usuario.registro.nome), render_to_string('template_email.html', context), emailconf.email, [c.email], fail_silently=False)
            clean_emails.append(e)
        return render_to_response("sent.html", {"user":request.user, "message":message, "clean":clean_emails, "emails":e, "pagina": "multiple_invites" }, context_instance=RequestContext(request))
    
    #Página para informar e-mails
    return render_to_response("multiple_invite.html", {"user":request.user, "message":message, "clean":clean_emails, "emails":e, "pagina": "multiple_invites" }, context_instance=RequestContext(request))


def createRegistro(user):
    """ Cria um registro vazio"""
    reg = Registro_Egresso()
    reg.curso = ""
    reg.matricula = ""
    reg.nome = ""
    reg.sexo = ""
    reg.nascimento = date(1900,01,01)
    reg.filiacao_ou_mae = ""
    reg.pai = ""
    reg.naturalidade1 = ""
    reg.naturalidade2 = ""
    reg.endereco = ""
    reg.bairro = ""
    reg.municipio = ""
    reg.cep = ""
    reg.telefone = ""
    reg.email = user.email
    reg.ingresso = ""
    reg.forma_ingresso = ""
    reg.evasao = ""
    reg.situacao = ""
    dados = Dados_Atualizados()
    dados.cidade=reg.municipio
    dados.data_atualizacao=timezone.now()
    dados.nome_Atual=reg.nome
    dados.ocupacao=""
    dados.onde_trabalha=""
    dados.pais=""
    dados.setor_atuacao=""
    dados.save()
    reg.dados_atuais=dados
    reg.save()
    usuario = Usuario()
    usuario.registro = reg
    usuario.usuario = user
    usuario.save()
    return usuario
    

# @login_required(login_url="/login/")
def save(request):
    status = "nada aconteceu"
    
    if request.POST:
        if request.user is not None:
            u = Usuario.objects.filter(usuario__id=request.user.id)[0]
            d = u.registro.dados_atuais
            d.nome_Atual = request.POST.get('nome_atual')
            d.cidade = request.POST.get('cidade')
            d.pais = request.POST.get('pais')
            d.onde_trabalha = request.POST.get('onde_trabalha')
            d.ocupacao = request.POST.get('ocupacao')
            d.setor_atuacao = request.POST.get('setor_atuacao')
            d.privacidade = request.POST.get('privacidade')
            d.data_atualizacao = timezone.now()
            d.save()
            r = u.registro
            r.pagina_web = request.POST.get('pagina_web')
            r.save()
            status = "Dados salvos"
            print u.registro.privacidade
        else:
            status = "Dados nao foram salvos"
    print status      
    return HttpResponseRedirect("/profile/"+str(request.user.usuario.id)) 
    
@login_required(login_url="/login/")
def edit(request):
    """
    Encaminha para a página de edição dos dados
    """
#     if not request.user.is_authenticated():    
#         return HttpResponseRedirect("/login/")
#     print request.user.registro
    return render_to_response("edit.html", {"pagina": "edit", "usuario": request.user.usuario}, context_instance=RequestContext(request))

def mylogout(request):
    """
    Realiza logout
    """
    logout(request)
    return HttpResponseRedirect("/") # redireciona o usuario logado para a pagina inicial


def registrar(request):
    """
    Realiza o cadastro de um egresso
    """
    # Se dados forem passados via POST
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
         
        if form.is_valid(): # se o formulario for valido
            form.save() # cria um novo usuario a partir dos dados enviados 
            return HttpResponseRedirect("/login/") # redireciona para a tela de login
        else:
            # mostra novamente o formulario de cadastro com os erros do formulario atual
            return render(request, "registrar.html", {"form": form })
     
    # se nenhuma informacao for passada, exibe a pagina de cadastro com o formulario
    return render(request, "registrar.html", {"form": UserCreationForm() })
 
 
def logar(request):
    """
    Realiza login
    """
    if request.user.is_authenticated():
        return HttpResponseRedirect("/")

    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            next = request.GET.get("next", "None")
            if next is not None and next != 'None':
                return HttpResponseRedirect(next)
            else:
                return HttpResponseRedirect("/home/")
            
        else:
            return render(request, "logar.html", {"form": form})
    return render(request, "logar.html", {"form": AuthenticationForm() })


def favicon(request):
    """
    Retorna o favicon. Favicons logotipos utilizados nas abas do navegador e na barra de favoritos. 
    """
    return HttpResponseRedirect("/static/logica/images/favicon.ico")


def merge(request):
    """
    Realiza a junção de dois registros
    """
    message = ''
    if request.POST:
        id = request.POST["id_outro_usuario"]
        outro_usuario = Usuario.objects.get(id=id)
        usuario = request.user.usuario
        if usuario.registro.equals(outro_usuario.registro) and outro_usuario.id != usuario.id:
            registro = usuario.registro.merge(outro_usuario.registro)
            outro_usuario.registro = registro
            usuario.registro.save()
            usuario.save()
            outro_usuario.registro.save()
            outro_usuario.save()
            message="Junção realizada com sucesso"
        elif outro_usuario.id == usuario.id:
            message="Não é possível realizar a junção de egresso com ele mesmo. Junção não realizada."
        else:
            message="Egressos parecem não ser iguais! Junção não realizada."
    return render_to_response("profile.html", {"user":request.user, "message":message, "usuario":request.user.usuario })