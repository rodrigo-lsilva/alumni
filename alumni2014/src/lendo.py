# encoding: UTF-8
""" 
Script que abre um arquivo Microsoft Excel, versão 2003, extensão xls (alunos_filtrados.xls), no seguinte formato:
Uma única planilha, como o nome "Exportar Planilha", contendo um aluno por linha, sendo que as 
colunas são:
CURSO, MATRICULA, NOME, SEXO, NASCIMENTO, FILIACAO_OU_MAE, PAI, NATURALIDADE1, NATURALIDADE2, ENDEREÇO, 
BAIRRO, MUNICIPIO, CEP, TELEFONE, EMAIL, INGRESSO, FORMA_INGRESSO, EVASAO, SITUACAO, UNIDADE_ACADEMICA(id)

Obs.: situação deve conter a informação GRADUACAO ou MESTRE ou DOUTOR

-----------------------------------------------------------------------
OBS.: A versão atual do python no servidor não suporta XLSX, apenas XLS
-----------------------------------------------------------------------
"""
import xlrd
import sys
from datetime import date, datetime
from django.utils import timezone

"""
Configuração necessária para acessar o django fora do servidor
"""
from django.conf import settings

settings.configure(
    DATABASES = { 'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'egressosdb',
        'USER': 'root',
        'PASSWORD': 'setPHYL43',
        'HOST': 'localhost',
        'PORT': '5432',
        }, },
    TIME_ZONE = 'America/New_York'
)

from egressos.logica.models import Registro_Egresso, Dados_Atualizados, Graduacao, Pos_Graduacao, UnidadeAcademica


def importXLStoDB(xls_filename='alunos_filtrados.xls'):
    print xls_filename
    workbook = xlrd.open_workbook(xls_filename)
    worksheet = workbook.sheet_by_name(u'Exportar Planilha')
    num_rows = worksheet.nrows
    num_cells = worksheet.ncols

    for i in range(1,num_rows):
        data = []
        for j in range(num_cells):
            data.append(worksheet.cell_value(i,j))
            
        print data
        print len(data)
        if data[18].upper().startswith('GRADUAD') or data[18].upper().startswith('MESTRE') or data[18].upper().startswith('DOUTOR'): 
            r = Registro_Egresso()
            r.nome = data[2]
            r.sexo = data[3]
            r.nascimento = datetime.strptime(data[4], "%d/%m/%Y %H:%M:%S").date()
            r.filiacao_ou_mae = data[5]
            r.pai = data[6]
            r.naturalidade1 = data[7]
            r.naturalidade2 = data[8]
            r.endereco = data[9]
            r.bairro = data[10]
            r.municipio = data[11]
            r.cep = data[12]
            r.telefone = data[13]
            r.email = data[14]
            dados = Dados_Atualizados()
            dados.cidade=r.municipio
            dados.data_atualizacao=timezone.now()
            dados.nome_Atual=r.nome
            dados.ocupacao=""
            dados.onde_trabalha=""
            dados.pais=""
            dados.setor_atuacao=""
            dados.save()
            r.dados_atuais=dados
            r.save()
            unidade=UnidadeAcademica.objects.get(id=data[19])
            #Lê e salva os dados do curso de graduação
            if data[18].upper().startswith('GRADUAD'):
                graduacao=Graduacao()
                graduacao.curso=data[0]
                graduacao.ingresso=data[15]
                graduacao.forma_ingresso=data[16]
                graduacao.evasao=data[17]
                graduacao.matricula=data[1]
                graduacao.outras_matriculas=""
                graduacao.situacao=data[18]
                graduacao.save()
                graduacao.unidadeAcademica.add(unidade)
                r.graduacao.add(graduacao)
                r.save()
                
            #Lê e salva os dados do curso de pós-graduação
            if data[18].upper().startswith('MESTR') or data[18].upper().startswith('DOUTOR'):
                pos=Pos_Graduacao()
                pos.programa=data[0]
                pos.ingresso=data[15]
                pos.forma_ingresso=data[16]
                pos.evasao=data[17]
                pos.matricula=data[1]
                pos.outras_matriculas=""
                pos.situacao=data[18]
                pos.unidadeAcademica.add(unidade)
                if data[18].upper().startswith('MESTR'):
                    pos.nivel=Pos_Graduacao.NIVEL_MESTRADO
                elif data[18].upper().startswith('DOUTOR'):
                    pos.nivel=Pos_Graduacao.NIVEL_DOUTORADO
                else:
                    pos.nivel=""
                pos.save()
                r.pos_graduacao.add(pos)
                r.save()
        
#importXLStoDB(xls_filename="/mnt/files/workspace/egressos/docs/evadidos CC 2013-1.xlsx")
print list
list=sys.argv
#print "Importando conteúdo de ", list[1]
importXLStoDB(xls_filename=list[1])