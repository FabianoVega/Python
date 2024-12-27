menu = """

[d] Depositar
[s] Sacar
[e] Extrato
[q] Sair

=> """

saldo = 0
limite = 500
extrato = ""
numero_saques = 0
LIMITE_SAQUES = 3




while True:

    opcao = input(menu)

    if opcao == 'd':
        valor= float(input('Digite a quantia a ser depositado: '))
        if valor > 0:
            saldo +=valor
            extrato += f'Extrato:{valor:.2f}\n'
        else:
            print('Operação falhou pois o valor informado é invalido')    
    elif opcao == 's':

        valor = float(input('Digite o valor do saque:'))

        excedeu_valor = valor > saldo
        excedeu_limite = valor > limite
        excedeu_saque = numero_saques>=LIMITE_SAQUES

        if excedeu_valor:
            print('Não a saldo suficiente.')
        elif excedeu_limite:
            print('Limite de R$500,00 ultrapassado.')
        elif excedeu_saque:
            print('Excedeu o limite de saques.')
        elif valor > 0:
            saldo -= valor
            extrato += f'Extrato:{valor:.2f}\n'
            numero_saques+=1
        else:
            print('Valor invalido, tente novamente.')
    
    elif opcao == 'e':
        print("\n================ EXTRATO ================")
        print("Não foram realizadas movimentações." if not extrato else extrato)   #É uma expressão condicional que verifica se a variável extrato está vazia (ou seja, se não houver nenhuma movimentação registrada).
        print(f"\nSaldo: R$ {saldo:.2f}")
        print("==========================================")
    

    elif opcao == 'q':
        break
    else:
        print('Opção na existe. tente novamente.')
        
