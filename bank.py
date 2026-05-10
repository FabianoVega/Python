#  Simulador de sistema bancário com funcionalidades de depósito, saque, extrato, criação de conta e cliente, e listagem de contas.
# O código utiliza classes para representar clientes, contas e transações, além de um iterador para percorrer as contas.
# O menu principal permite ao usuário interagir com o sistema e realizar as operações desejadas.



from abc import ABC, abstractmethod
from datetime import datetime
import textwrap


#serve pra percorrer as contas uma por uma
class ContasIterador:
    def __init__(self, contas):
        self.contas = contas
        self._index = 0

    def __iter__(self):
        return self

    # pega a próxima conta da lista
    def __next__(self):
        try:
            conta = self.contas[self._index]

            return f"""\
Agência:\t{conta.agencia}
Número:\t\t{conta.numero}
Titular:\t{conta.cliente.nome}
Saldo:\t\tR$ {conta.saldo:.2f}
"""

        except IndexError:
            raise StopIteration

        finally:
            self._index += 1


# classe base dos clientes
class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    # faz a transação na conta
    def realizar_transacao(self, conta, transacao):

        # limite de transações no dia
        if len(conta.historico.transacoes_do_dia()) >= 10:
            print("\n@@@ Você excedeu o número de transações permitidas para hoje! @@@")
            return

        transacao.registrar(conta)

    # adiciona conta pro cliente
    def adicionar_conta(self, conta):
        self.contas.append(conta)


# cliente pessoa física
class PessoaFisica(Cliente):
    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(endereco)

        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf

    # como o objeto vai aparecer no print
    def __repr__(self):
        return f"<{self.__class__.__name__}: ('{self.cpf}')>"


# classe principal da conta
class Conta:
    def __init__(self, numero, cliente):

        # atributos protegidos
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

    # cria nova conta
    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)

    # getters
    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico

    # saque normal
    def sacar(self, valor):

        excedeu_saldo = valor > self.saldo

        if excedeu_saldo:
            print("\n@@@ Operação falhou! Você não tem saldo suficiente. @@@")

        elif valor > 0:
            self._saldo -= valor

            print("\n=== Saque realizado com sucesso! ===")

            return True

        else:
            print("\n@@@ Operação falhou! O valor informado é inválido. @@@")

        return False

    # depósito
    def depositar(self, valor):

        if valor > 0:
            self._saldo += valor

            print("\n=== Depósito realizado com sucesso! ===")

            return True

        print("\n@@@ Operação falhou! O valor informado é inválido. @@@")

        return False


# conta corrente herdando da conta principal
class ContaCorrente(Conta):

    def __init__(self, numero, cliente, limite=500, limite_saques=3):

        # pega tudo da classe pai
        super().__init__(numero, cliente)

        self._limite = limite
        self._limite_saques = limite_saques

    @classmethod
    def nova_conta(cls, cliente, numero, limite, limite_saques):
        return cls(numero, cliente, limite, limite_saques)

    # sobrescrevendo o método sacar
    def sacar(self, valor):

        # conta quantos saques já teve
        numero_saques = len(
            [
                transacao
                for transacao in self.historico.transacoes
                if transacao["tipo"] == Saque.__name__
            ]
        )

        excedeu_limite = valor > self._limite
        excedeu_saques = numero_saques >= self._limite_saques

        if excedeu_limite:
            print("\n@@@ Operação falhou! O valor do saque excede o limite. @@@")

        elif excedeu_saques:
            print("\n@@@ Operação falhou! Número máximo de saques excedido. @@@")

        else:
            return super().sacar(valor)

        return False

    def __repr__(self):
        return f"<{self.__class__.__name__}: ('{self.agencia}', '{self.numero}', '{self.cliente.nome}')>"

    # define como a conta aparece no print
    def __str__(self):
        return f"""\
Agência:\t{self.agencia}
C/C:\t\t{self.numero}
Titular:\t{self.cliente.nome}
"""


# salva histórico das transações
class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    # adiciona transação na lista
    def adicionar_transacao(self, transacao):

        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            }
        )

    # yield pra retornar uma transação por vez
    def gerar_relatorio(self, tipo_transacao=None):

        for transacao in self._transacoes:

            if (
                tipo_transacao is None
                or transacao["tipo"].lower() == tipo_transacao.lower()
            ):

                yield transacao

    # pega só as transações do dia
    def transacoes_do_dia(self):

        data_atual = datetime.now().date()

        return [
            transacao
            for transacao in self._transacoes
            if datetime.strptime(
                transacao["data"], "%d-%m-%Y %H:%M:%S"
            ).date()
            == data_atual
        ]


# classe abstrata
class Transacao(ABC):

    # obriga as classes filhas terem valor
    @property
    @abstractmethod
    def valor(self):
        pass

    # obriga implementar registrar
    @abstractmethod
    def registrar(self, conta):
        pass


# saque
class Saque(Transacao):

    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    # faz saque e salva histórico
    def registrar(self, conta):

        sucesso = conta.sacar(self.valor)

        if sucesso:
            conta.historico.adicionar_transacao(self)


# depósito
class Deposito(Transacao):

    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    # faz depósito e salva histórico
    def registrar(self, conta):

        sucesso = conta.depositar(self.valor)

        if sucesso:
            conta.historico.adicionar_transacao(self)


# decorator pra mostrar log da função
def log_transacao(func):

    def envelope(*args, **kwargs):

        resultado = func(*args, **kwargs)

        data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        print(f"{data_hora}: {func.__name__.upper()}")

        return resultado

    return envelope


# menu principal
def menu():

    menu_texto = """
================ MENU ================
[d]\tDepositar
[s]\tSacar
[e]\tExtrato
[nc]\tNova conta
[lc]\tListar contas
[nu]\tNovo usuário
[q]\tSair
=> """

    return input(textwrap.dedent(menu_texto))


# procura cliente pelo cpf
def filtrar_cliente(cpf, clientes):

    clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]

    return clientes_filtrados[0] if clientes_filtrados else None


# deixa escolher qual conta usar
def recuperar_conta_cliente(cliente):

    if not cliente.contas:
        print("\n@@@ Cliente não possui conta! @@@")
        return None

    print("\nContas disponíveis:")

    for i, conta in enumerate(cliente.contas):
        print(f"[{i}] Conta: {conta.numero}")

    indice = int(input("Escolha a conta: "))

    try:
        return cliente.contas[indice]

    except IndexError:
        print("\n@@@ Conta inválida! @@@")
        return None


# função de depósito
@log_transacao
def depositar(clientes):

    cpf = input("Informe o CPF do cliente: ")

    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return

    valor = float(input("Informe o valor do depósito: "))

    conta = recuperar_conta_cliente(cliente)

    if not conta:
        return

    transacao = Deposito(valor)

    cliente.realizar_transacao(conta, transacao)


# função de saque
@log_transacao
def sacar(clientes):

    cpf = input("Informe o CPF do cliente: ")

    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return

    valor = float(input("Informe o valor do saque: "))

    conta = recuperar_conta_cliente(cliente)

    if not conta:
        return

    transacao = Saque(valor)

    cliente.realizar_transacao(conta, transacao)


# mostra extrato
@log_transacao
def exibir_extrato(clientes):

    cpf = input("Informe o CPF do cliente: ")

    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return

    conta = recuperar_conta_cliente(cliente)

    if not conta:
        return

    print("\n================ EXTRATO ================")

    extrato = ""
    tem_transacao = False

    for transacao in conta.historico.gerar_relatorio():

        tem_transacao = True

        extrato += (
            f"\n{transacao['data']}"
            f"\n{transacao['tipo']}:"
            f"\n\tR$ {transacao['valor']:.2f}"
        )

    if not tem_transacao:
        extrato = "Não foram realizadas movimentações"

    print(extrato)

    print(f"\nSaldo:\n\tR$ {conta.saldo:.2f}")

    print("==========================================")


# cria cliente
@log_transacao
def criar_cliente(clientes):

    cpf = input("Informe o CPF: ")

    cliente = filtrar_cliente(cpf, clientes)

    if cliente:
        print("\n@@@ Já existe cliente com esse CPF! @@@")
        return

    nome = input("Informe o nome completo: ")
    data_nascimento = input("Informe a data de nascimento: ")
    endereco = input("Informe o endereço: ")

    cliente = PessoaFisica(
        nome=nome,
        data_nascimento=data_nascimento,
        cpf=cpf,
        endereco=endereco,
    )

    clientes.append(cliente)

    print("\n=== Cliente criado com sucesso! ===")


# cria conta
@log_transacao
def criar_conta(numero_conta, clientes, contas):

    cpf = input("Informe o CPF do cliente: ")

    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return

    conta = ContaCorrente.nova_conta(
        cliente=cliente,
        numero=numero_conta,
        limite=500,
        limite_saques=3,
    )

    contas.append(conta)

    cliente.adicionar_conta(conta)

    print("\n=== Conta criada com sucesso! ===")


# lista contas
def listar_contas(contas):

    for conta in ContasIterador(contas):

        print("=" * 100)

        print(textwrap.dedent(conta))


# função principal do sistema
def main():

    clientes = []
    contas = []

    while True:

        opcao = menu()

        if opcao == "d":
            depositar(clientes)

        elif opcao == "s":
            sacar(clientes)

        elif opcao == "e":
            exibir_extrato(clientes)

        elif opcao == "nu":
            criar_cliente(clientes)

        elif opcao == "nc":

            numero_conta = len(contas) + 1

            criar_conta(numero_conta, clientes, contas)

        elif opcao == "lc":
            listar_contas(contas)

        elif opcao == "q":
            break

        else:
            print("\n@@@ Operação inválida! @@@")


main()