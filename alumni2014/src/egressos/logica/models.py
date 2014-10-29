# encoding: UTF-8
# from random import randint
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date
from egressos.logica.util import ano_inicial, getProximoAno
from django.db.models.aggregates import Count
import sys

# Arquivo que armazena o id do domínio. Essa informação é utilizada para gerar a página inicial 
view = "view"

def getID():
    """
    Lê o conteúdo do arquivo ID
    """
    file = open(view, "r")
    id = file.read()
    file.close()
    return id


def getUltimosCadastrados():
    """
    Recupera os últimos dez usuários cadastrados no sistema
    """
    out=""
    for u in Usuario.objects.all()[::-1][:10]:
        if u.__unicode__() != None:
            out+="<br><a href=\"/profile/" + str(u.id) +"\">" + str(u.__unicode__()) + "</a>"
    return out


def getDominio():
    """
    Obtém o domínio local
    @return: Retorna um domínio, caso o mesmo esteja definido no arquivo de configuração. Em caso contrário retorna None. 
    """
    try:
        return Dominio.objects.get(id=getID())
    except:
        print sys.exc_info()[0]
        return None

def setID(id):
    """
    Grava o id para o arquivo ID
    """
    file = open(view, "w")
    id = file.write(id)
    file.flush()
    file.close()
    


class Estatisticas():
    """
    Classe que armazena dados estatísticos sobre um centro ou unidade acadêmica
    """
    total_egressos = 0
    total_graduacao = 0
    total_pos_graduacao = 0
    total_cadastrados = 0
    periodo_mais_egressos_graduacao = 0
    periodo_mais_egressos_pos_graduacao = 0
    periodo_menos_egressos_graduacao = 0
    periodo_menos_egressos_pos_graduacao = 0
    #     Lista de dicionários: total, ano_evasao
    total_egressos_graduacao_por_evasao = []
    total_usuarios_registrados_graduacao_por_evasao = []
    #     Lista de dicionários: total, ano_evasao, mestre, doutores
    total_egressos_pos_graduacao_por_evasao = []
    total_usuarios_registrados_pos_graduacao_por_evasao = []
    # Curso de graduação
    egressos_por_curso = []
    # Programa de pós-graduação
    egressos_por_programa = []
    
    
    def getDados(self, dominio):
        """
        Calcula os dados
        """
        dominio = getDominio()
        self.total_cadastrados = len(Usuario.objects.all())
        if dominio != None:
            if dominio.isCentro:
                # As estatísticas do centro incluem todos os cursos do centro
                total_g = len(Graduacao.objects.filter(unidadeAcademica__centro__id=dominio.centro.id))
                total_pg = len(Pos_Graduacao.objects.filter(unidadeAcademica__centro__id=dominio.centro.id))
                self.total_egressos += total_g + total_pg
                self.total_graduacao += total_g
                self.total_pos_graduacao = total_pg
                self.egressos_por_curso = Graduacao.objects.filter(unidadeAcademica__centro__id=dominio.centro.id).values('curso').annotate(total=Count('curso')).order_by('curso')
                self.egressos_por_programa = Pos_Graduacao.objects.filter(unidadeAcademica__centro__id=dominio.centro.id).values('programa').annotate(total=Count('programa')).order_by('programa')
                self.total_egressos_graduacao_por_evasao = Graduacao.objects.filter(unidadeAcademica__centro__id=dominio.centro.id).values('evasao').annotate(total=Count('evasao')).order_by('evasao')
                # Calcula o total de usuários que realizaram graduação e estão cadastrados, por ano
                for i in self.total_egressos_graduacao_por_evasao:
                    total = len(Usuario.objects.filter(registro__graduacao__evasao=str(i['evasao'])).filter(registro__graduacao__unidadeAcademica__centro__id=dominio.centro.id).distinct())
                    self.total_usuarios_registrados_graduacao_por_evasao.append({"evasao":i['evasao'], "total":total})
                
                # Cria uma lista contendo todos os egressos da pós-graduação
                for i in range(ano_inicial, getProximoAno()):
                    m = Pos_Graduacao.objects.filter(evasao__year=i).filter(nivel=Pos_Graduacao.NIVEL_MESTRADO).filter(unidadeAcademica__centro__id=dominio.centro.id).aggregate(total=Count('evasao'))
                    d = Pos_Graduacao.objects.filter(evasao__year=i).filter(nivel=Pos_Graduacao.NIVEL_DOUTORADO).filter(unidadeAcademica__centro__id=dominio.centro.id).aggregate(total=Count('evasao'))
                    total = m['total'] + d['total']
                    self.total_egressos_pos_graduacao_por_evasao.append({'total': total, 'evasao':i, 'mestres': m['total'], 'doutores': d['total']})
                    cadastrados = len(Usuario.objects.filter(registro__pos_graduacao__evasao__year=i).filter(registro__graduacao__unidadeAcademica__centro__id=dominio.centro.id).distinct())
                    self.total_usuarios_registrados_pos_graduacao_por_evasao.append({'evasao':i, 'total':cadastrados})
                    
                # Determina o período com mais e menos egressos na graduação
                max = 0
                min = 100000
                for g in self.total_egressos_graduacao_por_evasao:
                    if g['total'] > max:
                        max = g['total'] 
                        self.periodo_mais_egressos_graduacao = g['evasao']
                    if g['total'] < min and g['total'] > 0:
                        min = g['total']
                        self.periodo_menos_egressos_graduacao = g['evasao']
                        
                # Determina o período com mais e menos egressos na pós-graduação
                max = 0
                min = 100000
                for g in self.total_egressos_pos_graduacao_por_evasao:
                    if g['total'] > max:
                        max = g['total'] 
                        self.periodo_mais_egressos_pos_graduacao = g['evasao']
                    if g['total'] < min and g['total'] > 0:
                        min = g['total']
                        self.periodo_menos_egressos_pos_graduacao = g['evasao']
            
            elif dominio.isCentro == False:
                # As estatísticas da unidade acadêmica incluem apenas os cursos da unidade
                total_g = len(Graduacao.objects.filter(unidadeAcademica__id=dominio.unidadeAcademica.id))
                total_pg = len(Pos_Graduacao.objects.filter(unidadeAcademica__id=dominio.unidadeAcademica.id))
                self.total_egressos += total_g + total_pg
                self.total_graduacao += total_g
                self.total_pos_graduacao = total_pg
                self.total_egressos_graduacao_por_evasao = Graduacao.objects.filter(unidadeAcademica__id=dominio.unidadeAcademica.id).values('evasao').annotate(total=Count('evasao')).order_by('evasao')
                self.egressos_por_curso = Graduacao.objects.filter(unidadeAcademica__id=dominio.unidadeAcademica.id).values('curso').annotate(total=Count('curso')).order_by('curso')
                self.egressos_por_programa = Pos_Graduacao.objects.filter(unidadeAcademica__id=dominio.unidadeAcademica.id).values('programa').annotate(total=Count('programa')).order_by('programa')
                
                # Calcula o total de usuários que realizaram graduação e estão cadastrados, por ano
                for i in self.total_egressos_graduacao_por_evasao:
                    total = len(Usuario.objects.filter(registro__graduacao__evasao=str(i['evasao'])).filter(registro__graduacao__unidadeAcademica__id=dominio.id).distinct())
                    self.total_usuarios_registrados_graduacao_por_evasao.append({"evasao":i['evasao'], "total":total})
                
                
                # Cria uma lista contendo todos os egressos da pós-graduação
                for i in range(ano_inicial, getProximoAno()):
                    m = Pos_Graduacao.objects.filter(evasao__year=i).filter(nivel=Pos_Graduacao.NIVEL_MESTRADO).filter(unidadeAcademica__id=dominio.unidadeAcademica.id).aggregate(total=Count('evasao'))
                    d = Pos_Graduacao.objects.filter(evasao__year=i).filter(nivel=Pos_Graduacao.NIVEL_DOUTORADO).filter(unidadeAcademica__id=dominio.unidadeAcademica.id).aggregate(total=Count('evasao'))
                    total = m['total'] + d['total']
                    self.total_egressos_pos_graduacao_por_evasao.append({'total': total, 'evasao':i, 'mestres': m, 'doutores': d})
                    # Calcula o total de usuários que realizaram graduação e estão cadastrados, por ano
                    cadastrados = len(Usuario.objects.filter(registro__pos_graduacao__evasao__year=i).filter(registro__graduacao__unidadeAcademica__id=dominio.centro.id).distinct())
#                     cadastrados = len(Usuario.objects.filter(registro__pos_graduacao__evasao=str(i['evasao'])).filter(registro__pos_graduacao__unidadeAcademica__id=dominio.id).distinct())
                    self.total_usuarios_registrados_pos_graduacao_por_evasao.append({'evasao':i, 'total':cadastrados})
                    
                # Determina o período com mais e menos egressos na graduação
                max = 0
                min = 100000
                for g in self.total_egressos_graduacao_por_evasao:
                    if g['total'] > max:
                        max = g['total'] 
                        self.periodo_mais_egressos_graduacao = g['evasao']
                    if g['total'] < min and g['total'] > 0:
                        min = g['total']
                        self.periodo_menos_egressos_graduacao = g['evasao']
                        
                # Determina o período com mais e menos egressos na pós-graduação
                max = 0
                min = 100000
                for g in self.total_egressos_pos_graduacao_por_evasao:
                    if g['total'] > max:
                        max = g['total'] 
                        self.periodo_mais_egressos_pos_graduacao = g['evasao']
                    if g['total'] < min and g['total'] > 0:
                        min = g['total']
                        self.periodo_menos_egressos_pos_graduacao = g['evasao']
            
class Centro(models.Model):
    """
    Define um centro da universidade
    """
    nome = models.CharField(max_length=400)
    
    def __unicode__(self):
        return "Centro: " + str(self.nome)
    
class UnidadeAcademica(models.Model):
    """
    Define uma unidade acadêmica de um centro
    """
    nome = models.CharField(max_length=400)
    centro = models.ForeignKey('Centro')
    
    def __unicode__(self):
        return "UA: " + str(self.nome) + ", centro: " + str(self.centro.nome)
    

class Dados_Atualizados(models.Model):
    """
        Situação atualizada do egresso. Nesse objeto é armazenada a situação atual dos egressos.
    """
    nome_Atual = models.CharField(max_length=150)
    cidade = models.CharField(max_length=150)
    pais = models.CharField(max_length=80)
    onde_trabalha = models.CharField(max_length=150)
    ocupacao = models.CharField(max_length=100)
    setor_atuacao = models.CharField(max_length=150) 
    data_atualizacao = models.DateTimeField()
    
    def __unicode__(self):
        return self.nome_Atual + ", país: " + self.pais + ", cidade: " + self.cidade + ", ocupação: " + self.ocupacao + " - " + self.onde_trabalha + ", atualizado em: " + self.data_atualizacao.__str__()
        

class Graduacao(models.Model):
    """
        Curso de graduação realizado por um egresso.
    """
    curso = models.CharField(max_length=150)
    matricula = models.CharField(max_length=20)
    outras_matriculas = models.CharField(max_length=60)
    ingresso = models.CharField(max_length=20)
    forma_ingresso = models.CharField(max_length=100)
    evasao = models.CharField(max_length=20)
    situacao = models.CharField(max_length=150)
    observacao = models.CharField(max_length=1024, null=True)
    unidadeAcademica = models.ManyToManyField(UnidadeAcademica)
    
    def __unicode__(self):
        return "Curso: " + self.curso + ", matrícula: " + self.matricula + ", evasão:" + self.evasao
    
    def getNome(self):
        return self.curso
    
    def getIngressoFormatado(self):
        return self.ingresso
    
    def getEvasaoFormatada(self):
        return self.evasao
    
    
class Pos_Graduacao(models.Model):
    """
        Curso de pós-graduação realizado por um egresso.
    """
    NIVEL_MESTRADO = "MESTRADO"
    NIVEL_DOUTORADO = "DOUTORADO"
    programa = models.CharField(max_length=150)
    nivel = models.CharField(max_length=30)
    matricula = models.CharField(max_length=20)
    outras_matriculas = models.CharField(max_length=60)
    ingresso = models.DateField(null=True)
    forma_ingresso = models.CharField(max_length=100)
    evasao = models.DateField(null=True)
    situacao = models.CharField(max_length=150)
    unidadeAcademica = models.ManyToManyField(UnidadeAcademica)
    observacao = models.CharField(max_length=1024, null=True)
    
    def __unicode__(self):
        return "Programa: " + self.programa + ", nível: " + self.nivel + ", matrícula: " + self.matricula + ", evasão:" + self.evasao.strftime("%d/%m/%Y")
    
    def getNome(self):
        return self.programa
    
    def getIngressoFormatado(self):
        return self.ingresso.year
    
    def getEvasaoFormatada(self):
        return self.evasao.year
    

class Registro_Egresso(models.Model):
    """
        Registro de um egresso.
    """
    PRIVADO = "privado"
    nome = models.CharField(max_length=150)
    sexo = models.CharField(max_length=1)
    nascimento = models.DateField()
    filiacao_ou_mae = models.CharField(max_length=200)
    pai = models.CharField(max_length=100)
    naturalidade1 = models.CharField(max_length=50)
    naturalidade2 = models.CharField(max_length=50)
    endereco = models.CharField(max_length=150)
    bairro = models.CharField(max_length=100)
    municipio = models.CharField(max_length=100)
    cep = models.CharField(max_length=15)
    telefone = models.CharField(max_length=30)
    email = models.CharField(max_length=60)
    privacidade = models.CharField(max_length=50)
    pagina_web = models.CharField(max_length=50)
    dados_atuais = models.OneToOneField(Dados_Atualizados)
    graduacao = models.ManyToManyField(Graduacao)
    pos_graduacao = models.ManyToManyField(Pos_Graduacao)
    
    def __unicode__(self):
        return self.nome + " " + self.sexo + " " + self.nascimento.__str__() + " " + self.email 
  
    def eh_privado(self):
        """
            Determina se o perfil é privado ou público.
            @return: True se o perfil for privado e False em caso contrário.
        """
        return self.privacidade == Registro_Egresso.PRIVADO
  
    def web_ok(self):
        """
            Determina se a página web é válida. Uma página é considerada válida se a string iniciar com 'http://'.
            @return: True se a página for válida e False em caso contrário.
        """
        return self.pagina_web.startswith("http://")
  
    def equals(self, outro_egresso):
        """
            Realiza a verificação se dois Registro_Egresso são iguais. Dois egressos são aceitáveis como iguais
            se a data de nascimento possuir ao menos dois campos iguais.
            @return: True caso sejam igual e False em caso contrário. 
        """ 
        comp = 0
        if self.nascimento == None or outro_egresso.nascimento == None:
            comp = 5
        else:
            if self.nascimento.year == outro_egresso.nascimento.year:
                comp = comp + 1
                
            if self.nascimento.month == outro_egresso.nascimento.month:
                comp = comp + 1
                 
            if self.nascimento.day == outro_egresso.nascimento.day:
                comp = comp + 1
                
        return comp > 1
                 
#             if comp > 1:
#                 return True
#             else:
#                 return False
        
  
    def cadastrado(self):
        """
            Determina se o egresso realizou seu cadastro
            @return: True caso exista e False em caso contrário 
        """
        try:
            if self.usuario:
                return True
            else:
                return False
        except:
            return False
        
    def merge(self, outro_egresso):
        """
        Em alguns casos, um egresso possui dois Registro_Egresso. Esse método é responsável por verificar se 
        dois egressos são iguais e, em caso positivo, realizar a junção dos dois Registro_Egresso em um único Registro_Egresso.
        A junção atualiza os dados deste Registro_Egresso com o outro_egresso.
        @return: O registro atualizado se os dois egresso forem pertencentes ao mesmo usuário. Em caso contrário, returna None.   
        """
        if self.equals(outro_egresso):
            # Realiza o merge de dois egressos
            if self.bairro == '' or self.bairro == None:
                self.bairro = outro_egresso.bairro
            if self.cep == '' or self.cep == None:
                self.cep = outro_egresso.cep
            if self.nome == '' or self.nome == None:
                self.nome = outro_egresso.nome
            if self.sexo == '' or self.sexo == None:
                self.sexo = outro_egresso.sexo
            if self.nascimento == '' or self.nascimento == None:
                self.nascimento = outro_egresso.nascimento
            if self.filiacao_ou_mae == '' or self.filiacao_ou_mae == None:
                self.filiacao_ou_mae = outro_egresso.filiacao_ou_mae
            if self.pai == '' or self.pai == None:
                self.pai = outro_egresso.pai
            if self.naturalidade1 == '' or self.naturalidade1 == None:
                self.naturalidade1 = outro_egresso.naturalidade1
            if self.naturalidade2 == '' or self.naturalidade2 == None:
                self.naturalidade2 = outro_egresso.naturalidade2
            if self.endereco == '' or self.endereco == None:
                self.endereco = outro_egresso.endereco
            if self.municipio == '' or self.municipio == None:
                self.municipio = outro_egresso.municipio
            if self.cep == '' or self.cep == None:
                self.cep = outro_egresso.cep
            if self.telefone == '' or self.telefone == None:
                self.telefone = outro_egresso.telefone
            if self.pagina_web == '' or self.pagina_web == None:
                self.pagina_web = outro_egresso.pagina_web
            if self.privacidade == self.PRIVADO or outro_egresso.privacidade == self.PRIVADO:
                self.privacidade = self.PRIVADO
            # Mantém os dados mais atuais
            if self.dados_atuais.data_atualizacao < outro_egresso.dados_atuais.data_atualizacao:
                self.dados_atuais = outro_egresso.dados_atuaistexto
            for g in outro_egresso.graduacao.all():
                self.graduacao.add(g)
            for pg in outro_egresso.pos_graduacao.all():
                self.pos_graduacao.add(pg)
            return self
        else:
            return None
        
class Dominio(models.Model):
    """
    Define um domínio administrativo
    """
    isCentro = models.BooleanField()
    centro = models.OneToOneField(Centro)
    unidadeAcademica = models.OneToOneField(UnidadeAcademica)
    textoPaginaInicial = models.CharField(max_length=1000000)
    BBCode = ["[title]", "[/title]" ,"[p]", "[/p]", "[b]", "[/b]", "[i]", "[/i]", "[u]", "[/u]", "[url]", "[/url]", "[email]", "[/email]", "[img]","[left]", "[/left]", "[right]", "[/right]", "[center]", "[/center]", "[justify]", "[/justify]", "[br]"]
    BBCodeExplicacao = ["Inicia um título", "Encerra um título", "Inicia um parágrafo", "Encerra um parágrafo", "Inicia texto em negrito", "Encerra texto em negrito", "Inicia texto em itálico", "Encerra texto itálico", "Inicia texto sublinhado", "Encerra texto sublinhado", "Inseri um link: [url=http://www.exemplo.com]Texto do link[/url]", "Encerra o texto de um link", "Inseri um link para email: [email=email@exemplo.com]Texto do link[/email]", "Encerra o texto de um link para email", "Inseri uma imagem: [img=http://www.exemplo.com/imagem.jpg]", "Inicia texto com alinhamento à esquerda", "Encerra texto com alinhamento à esquerda", "Inicia texto com alinhamento à direita", "Encerra texto com alinhamento à direita", "Inicia texto com alinhamento centralizado", "Encerra texto com alinhamento centralizado" , "Inicia texto com alinhamento justificado", "Encerra texto com alinhamento justificado", "Quebra de linha (nova linha)"]
    variaveis = ["ultimos_usuarios", "total_egressos", "total_graduacao", "total_pos_graduacao", "periodo_mais_egressos_graduacao", "periodo_mais_egressos_pos_graduacao", "periodo_menos_egressos_graduacao", "periodo_menos_egressos_pos_graduacao", "total_cadastrados"]
    variaveisExplicacao = ["Lista contendo os 10 últimos usuários cadastrados", "Número total de egressos", "Número total de egressos na graduação", "Número total de egressos na pós-graduação" , "Período com mais egressos na graduacao", "Período com mais egressos na pós-graduacao", "Período com menos egressos na graduacao", "Período com menos egressos na pós-graduacao", "Cálculo o total de egressos cadastrados. Para essa variável, cadastrado significa egressos que acessam o sistema e atualizam seus dados"] 
    
    def getVariaveis(self):
        """
        Recupera a lista de variáveis disponíveis 
        """
        return self.variaveis
    
    def getVariaveisExplicacao(self):
        """
        Retorna uma lista bidimensional contendo com as variáveis e uma explicação sobre o valor da mesma. 
        """
        lista = []
        for i in range(0, len(self.variaveis)):
            lista.append("<span title=\"" + str(self.variaveisExplicacao[i]) + "\">" + str(self.variaveis[i]) + "</span>") 
        return lista
    
    
    def getBBCode(self):
        """
        Retorna a lista de códigos BB válidados, seguidos da descrição
        """
        return self.BBCode
    
    def getBBCodeExplicacacao(self):
        """
        Retorna uma lista bidimensional contendo com os códigos BB e um exemplo de uso
        """
        lista = []
        for i in range(0,len(self.BBCode)):
            lista.append("<span title=\"" + str(self.BBCodeExplicacao[i]) + "\">" + str(self.BBCode[i]) + "</span>")
        
        return lista
    
    def textoFormatado(self):
        """
        Realiza processamento sobre o texto da página inicial convertendo Código BB e variáveis para html.
        """
        try:
            tmp = self.textoPaginaInicial#.replace("<", "&lt;").replace(">", "&gt;")
            estat = Estatisticas()
            estat.getDados(self)
            tmp = tmp.replace("ultimos_usuarios", getUltimosCadastrados())
            tmp = tmp.replace("total_cadastrados", str(estat.total_cadastrados))
            tmp = tmp.replace("total_egressos", str(estat.total_egressos))
            tmp = tmp.replace("total_graduacao", str(estat.total_graduacao))
            tmp = tmp.replace("total_pos_graduacao", str(estat.total_pos_graduacao))
            tmp = tmp.replace("periodo_mais_egressos_graduacao", str(estat.periodo_mais_egressos_graduacao))
            tmp = tmp.replace("periodo_mais_egressos_pos_graduacao", str(estat.periodo_mais_egressos_pos_graduacao))
            tmp = tmp.replace("periodo_menos_egressos_graduacao", str(estat.periodo_menos_egressos_graduacao))
            tmp = tmp.replace("periodo_menos_egressos_pos_graduacao", str(estat.periodo_menos_egressos_pos_graduacao))
            tmp = tmp.replace("[p]", "<p>").replace("[P]", "<p>")
            tmp = tmp.replace("[/p]", "</p>").replace("[/P]", "</p>")
            tmp = tmp.replace("[b]", "<b>").replace("[B]", "<b>")
            tmp = tmp.replace("[/b]", "</b>").replace("[/B]", "</b>")
            tmp = tmp.replace("[i]", "<i>").replace("[I]", "<i>")
            tmp = tmp.replace("[/i]", "</i>").replace("[/I]", "</i>")
            tmp = tmp.replace("[u]", "<u>").replace("[U]", "<u>")
            tmp = tmp.replace("[/u]", "</u>").replace("[/U]", "</u>")
            tmp = tmp.replace("[url=", "<a target=\"_blank\" href=\"").replace("[URL=", "<a target=\"_blank\" href=\"")
            tmp = tmp.replace("[/url]", "</a>").replace("[/URL]", "</a>")
            tmp = tmp.replace("[email=", "<a target=\"_blank\" href=\"mailto:").replace("[EMAIL=", "<a target=\"_blank\" href=\"mailto:")
            tmp = tmp.replace("[/email]", "</a>").replace("[/EMAIL]", "</a>")
            tmp = tmp.replace("[img=", "<img style=\"border: 0;\" src=\"").replace("[IMG=", "<img style=\"border: 0;\" src=\"")
            tmp = tmp.replace("[left]", "<div style=\"text-align: left\">").replace("[LEFT]", "<div style=\"text-align: left\">")
            tmp = tmp.replace("[left]", "</div>").replace("[LEFT]", "</div>")
            tmp = tmp.replace("[right]", "<div style=\"text-align: right\">").replace("[RIGHT]", "<div style=\"text-align: right\">")
            tmp = tmp.replace("[right]", "</div>").replace("[RIGHT]", "</div>")
            tmp = tmp.replace("[center]", "<div style=\"text-align: center\">").replace("[CENTER]", "<div style=\"text-align: center\">")
            tmp = tmp.replace("[center]", "</div>").replace("[CENTER]", "</div>")
            tmp = tmp.replace("[justify]", "<div style=\"text-align: justify\">").replace("[JUSTIFY]", "<div style=\"text-align: justify\">")
            tmp = tmp.replace("[justify]", "</div>").replace("[JUSTIFY]", "</div>")
            tmp = tmp.replace("[br]", "<br>").replace("[BR]", "<br>")
            tmp = tmp.replace("[title]", "<h2>").replace("[TITLE]", "<h2>")
            tmp = tmp.replace("[/title]", "</h2>").replace("[/TITLE]", "</h2>")
            # Precisa ser executado por último para garantir que os "]" de [url], [email] e [img] sejam removidos
            tmp = tmp.replace("]", "\">")
            return tmp
        except:
            print sys.exc_info()[0]
            return ""
    
    def __unicode__(self):
        return "id=" + str(self.id) + ", " + self.unidadeAcademica.__unicode__()


class Usuario(models.Model):
    usuario = models.OneToOneField(User) 
    registro = models.OneToOneField(Registro_Egresso)
    dominios = models.ManyToManyField(Dominio)
    # nome = Registro_Egresso(registro).nome
    # curso = Registro_Egresso(registro).curso
    # matricula = Registro_Egresso(registro).matricula
    # sexo = Registro_Egresso(registro).sexo
    # ingresso = Registro_Egresso(registro).ingresso
    # evasao = Registro_Egresso(registro).evasao
    # nome_atual = models.CharField(max_length=100)
    # email = models.CharField(max_length=50)
    # senha = models.CharField(max_length=50)
    # cidade = models.CharField(max_length=50)
    # pais = models.CharField(max_length=50)
    # onde_trabalha = models.CharField(max_length=50)
    # ocupacao = models.CharField(max_length=50)
    # setor_atucao = models.CharField(max_length=50)
    
    def isAdministrador(self):
        """
        Um usuário é defino como administrador se ele possui algum domínio associado
        com o seu usuário
        """
        return len(self.dominios.all()) > 0
    
    def isAdministradorDominio(self, dominio):
        """
        Determina se um usuário é administrador de um domínio
        """
        admin = False
        for d in self.dominios.all():
            if d.id == dominio.id:
                admin = True
        return admin
    
    def temPermissao(self, id):
        """
        Define se um usuário tem permissão para administrar um domínio
        """
        bool = False
        for p in self.dominios.all():
            if p.id == id:
                bool = True
                
        return bool
    
    
    def __unicode__(self):
        out = None
        try:
            out = self.registro.dados_atuais.nome_Atual
        except:
            print "Dados atuais não localizados"
        return out
    
    def merge(self, outro_usuario):
        """
            Realiza a junção dos registros de dois usuários diferentes. Um mesmo egresso poderá ter cursado 
            mais de um curso na mesma universidade. Para evitar que o mesmo precise manter dois ou mais registros
            atualizados e para garantir que todos os dados de um mesmo candidato seja unificados, esse método permite
            realizar a junção dos registros. Porém, nenhum usuário será excluído. 
        """
        self.registro;
        registro_merge = self.registro.merge(outro_usuario.registro)
        self.registro = registro_merge
        outro_usuario.registro = registro_merge

class Convite(models.Model):
    de = models.ForeignKey(Usuario)
    para = models.ForeignKey(Registro_Egresso)
    email = models.CharField(max_length=50)
    status = models.CharField(max_length=10)
    chave = models.CharField(max_length=80)
    ok = "ok"
    pendente = "pendente"
    
    def __unicode__(self):
        if self.de.registro == self.para:
            return " DE: " + self.de.__unicode__() + " | PARA EMAIL : " + self.email + " | STATUS: " + self.status
        return " DE: " + self.de.__unicode__() + " | PARA: " + self.para.__unicode__() + " | EMAIL: " + self.email + " | STATUS: " + self.status

    def is_ok(self):
        return "ok" == self.status
