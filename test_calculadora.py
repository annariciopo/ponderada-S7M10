import pytest
from calculadora import somar, subtrair, multiplicar, dividir


def test_somar():
    assert somar(2, 3) == 5
    assert somar(-1, 1) == 0
    assert somar(1.5, 2.5) == 4.0


def test_subtrair():
    assert subtrair(10, 5) == 5
    assert subtrair(0, 5) == -5


def test_multiplicar():
    assert multiplicar(3, 4) == 12
    assert multiplicar(-2, 3) == -6


def test_dividir_sucesso():
    assert dividir(10, 2) == 5
    assert dividir(5, 2) == 2.5


def test_dividir_por_zero():
    with pytest.raises(ValueError, match="Não é possível dividir por zero."):
        dividir(10, 0)
