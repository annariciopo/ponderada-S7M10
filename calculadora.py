import os

def somar(a, b):
    return a + b


def subtrair(a, b):
    return a - b


def multiplicar(a, b):
    return a * b


def dividir(a, b):
    if b == 0:
        raise ValueError("Não é possível dividir por zero.")
    return a / b


# Interface do usuário
def iniciar_calculadora():
    while True:
        print("\n--- CALCULADORA ---")
        print("1. Somar (+)")
        print("2. Subtrair (-)")
        print("3. Multiplicar (*)")
        print("4. Dividir (/)")
        print("5. Sair")

        escolha = input("Escolha uma opção (1-5): ")

        if escolha == '5':
            print("Encerrando a calculadora. Até mais!")
            break

        if escolha in ('1', '2', '3', '4'):
            try:
                num1 = float(input("Digite o primeiro número: "))
                num2 = float(input("Digite o segundo número: "))
            except ValueError:
                print("Erro: Digite apenas números válidos.")
                continue

            try:
                if escolha == '1':
                    print(f"Resultado: {somar(num1, num2)}")
                elif escolha == '2':
                    print(f"Resultado: {subtrair(num1, num2)}")
                elif escolha == '3':
                    print(f"Resultado: {multiplicar(num1, num2)}")
                elif escolha == '4':
                    print(f"Resultado: {dividir(num1, num2)}")
            except ValueError as e:
                print(f"Erro: {e}")
        else:
            print("Opção inválida! Tente novamente.")


if __name__ == "__main__":
    iniciar_calculadora()
