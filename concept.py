class Concept(object):

	def __init__(self, name='',var_set=set(),partners=[],sent_index=0,lable=''):
		self.name = name
		self.var_set = var_set
		try: partners.remove(self.name)
		except:	pass
		self.partners = partners
		self.sent_index = sent_index
		self.lable = lable

	def set_name(self,name=''):
		self.name = name

	def set_var_set(self,var_set=set()):
		self.var_set = var_set

	def set_partners(self,partners=[]):
		try: partners.remove(self.name)
		except:	pass
		self.partners = partners

	def set_sent_index(self,sent_index):
		self.sent_index = sent_index

	def add_partners(self,partners_to_add=[]):
		try: partners_to_add.remove(self.name)
		except:	pass
		self.partners = self.partners + partners_to_add

	def set_lable(self,lable=''):
		self.lable = lable
