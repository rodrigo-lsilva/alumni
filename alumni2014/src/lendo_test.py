# encoding: UTF-8
""" 
Script que abre um arquivo Microsoft Excel, versão 2003, extensão xls (alunos_filtrados.xls), no seguinte formato:
Uma única planilha, como o nome "Exportar Planilha", contendo um aluno por linha, sendo que as 
colunas são:
CURSO, MATRICULA, NOME, SEXO, NASCIMENTO, FILIACAO_OU_MAE, PAI, NATURALIDADE1, NATURALIDADE2, ENDEREÇO, 
BAIRRO, MUNICIPIO, CEP, TELEFONE, EMAIL, INGRESSO, FORMA_INGRESSO, EVASAO, SITUACAO
Os dados lidos dos arquivos são importados na tabela logica_registro_egresso
"""
import xlrd
from logica.models import Registro_Egresso

def importXLStoDB(xls_filename='/mnt/files/workspace/egressos/src/alunos_filtrados_test.xls'):
    workbook = xlrd.open_workbook(xls_filename)
    worksheet = workbook.sheet_by_name(u'Exportar Planilha')
    num_rows = worksheet.nrows
    num_cells = worksheet.ncols

    for i in range(1,num_rows):
        print i
        data = []
        for j in range(num_cells):
            data.append(worksheet.cell_value(i,j))
        r = Registro_Egresso()
        r.curso = data[0]
        r.matricula = data[1]
        r.nome = data[2]
        r.sexo = data[3]
        r.nascimento = data[4]
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
        r.ingresso = data[15]
        r.forma_ingresso = data[16]
        r.evasao = data[17]
        r.situacao = data[18]
        r.save()
        
        
importXLStoDB()