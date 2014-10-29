class convite :
	'''(NULL)'''
	def __init__(self) :
		self.de = None # 
		self.para = None # 
		self.email = None # 
		self.status = None # 
		self.key = None # 
		pass
	def __unicode__ (self) :
		# returns 
		pass
	def is_ok (self) :
		# returns 
		pass
class Registro_Egresso :
	'''(NULL)'''
	def __init__(self) :
		self.curso = None # 
		self.matricula = None # 
		self.outras_matriculas = None # 
		self.nome = None # 
		self.sexo = None # 
		self.nascimento = None # 
		self.filiacao_ou_mae = None # 
		self.pai = None # 
		self.naturalidade1 = None # 
		self.naturalidade2 = None # 
		self.endereco = None # 
		self.bairro = None # 
		self.municipio = None # 
		self.cep = None # 
		self.telefone = None # 
		self.email = None # 
		self.ingresso = None # 
		self.forma_ingresso = None # 
		self.evasao = None # 
		self.situacao = None # 
		pass
	def __unicode__ (self) :
		# returns 
		pass
	def cadastrado (self) :
		# returns 
		pass
class Usuario :
	'''(NULL)'''
	def __init__(self) :
		self.usuario = None # django.contrib.auth.models.User
		self.registro = None # logica.Registro_Egresso
		self.nome_atual = None # CharField
		self.cidade = None # CharField
		self.pais = None # CharField
		self.onde_trabalha = None # CharField
		self.ocupacao = None # CharField
		self.setor_atucao = None # CharField
		self.privacidade = None # CharField
		self.pagina_web = None # CharField
		pass
	def __unicode__ (self) :
		# returns 
		pass
	def eh_privado (self) :
		# returns 
		pass
	def  web_ok (self) :
		# returns 
		pass
