from typing import Tuple, Set, Dict, List, Union


class ErroException(Exception):
    """Aqui crio uma exceção personalizada.

    Args:
        mensagem (str): descrição do erro encontrado.
    """

    def __init__(self, mensagem):
        """Aqui inicializa a exceção.

        Args:
            mensagem (str): Mensagem do erro.
        """
        self.mensagem = mensagem
        super().__init__(self.mensagem)


def load_automata(filename: str) -> Tuple[
    Set[str], Set[str], Dict[Tuple[str, str], Union[str, List[str]]], str, Set[str]
]:
    """Aqui carrega um autômato a partir de um arquivo."""
    
    try:
        with open(filename, encoding='utf-8') as arquivo:
            linhas = arquivo.readlines()

            if len(linhas) < 5:
                raise ErroException("Arquivo não é autômato.")

            alfabeto = linhas[0].strip().split()
            estados = linhas[1].strip().split()
            estados_finais = linhas[2].strip().split()
            estado_inicial = linhas[3].strip()
            transicao = [linha.strip().split() for linha in linhas[4:]]

            transicoes = {}

            for estado in estados:
                transicoes[transicoes] = []
                for simbolo in alfabeto:
                    transicoes[estado][simbolo] = None

            for origem, simbolo, destino in transicao:
                if origem in estados and simbolo in alfabeto and destino in estados:
                    transicao[origem][simbolo] = destino
                else:
                    raise ErroException("Transição inválida.")

            for estado in estados_finais:
                if estado not in estados:
                    raise ErroException("Estado final não encontrado.")

            if estado_inicial not in estados:
                raise ErroException("Estado inicial não encontrado")

            automata = alfabeto, estados, transicao, estado_inicial, estados_finais
            return automata

    except FileNotFoundError as e:
        raise FileNotFoundError(f"Arquivo {filename} não encontrado.") from e


def process(automata: Tuple[Set[str], Set[str], Dict[Tuple[str, str], Union[str, List[str]]], str, Set[str]], words: List[str]) -> Dict[str, str]:
    """Aqui cria função."""

    _, sigma, _, _, _ = automata
    dfa = convert_to_dfa(automata)
    _, _, dfa_transicao, dfa_inicial, dfa_final = dfa

    verifica = {}
    try:
        for word in words:
            estado_atual = dfa_inicial
            verificacao = True

            for simbolo in word:
                if simbolo not in sigma and simbolo != '&':
                    verifica[word] = "INVÁLIDA"
                    verificacao = False
                    break

                if (estado_atual, simbolo) in dfa_transicao:
                    estado_atual = dfa_transicao[(estado_atual, simbolo)]
                else:
                    verifica[word] = "REJEITA"
                    verificacao = False
                    break

                if verificacao:
                    if estado_atual in dfa_final:
                        verifica[word] = "ACEITA"
                    else:
                        verifica[word] = "REJEITA"
        return verifica
    except Exception as e:
        raise ErroException(f"Erro ao processar palavra '{word}': {e}.") from e


def epsilon_closure(
    state: str, delta: Dict[Tuple[str, str], Union[str, List[str]]]
) -> Set[str]:
    """Aqui cria função."""

    closure = {state}
    stack = [state]
    while stack:
        estado_atual = stack.pop()
        if (estado_atual, '&') in delta:
            destinations = delta[(estado_atual, '&')]
            if isinstance(destinations, str):
                destinations = [destinations]
            for dest in destinations:
                if dest not in closure:
                    closure.add(dest)
                    stack.append(dest)
    return closure


def convert_to_dfa(
    automata: Tuple[Set[str], Set[str], Dict[Tuple[str, str], Union[str, List[str]]], str, Set[str]]
) -> Tuple[Set[str], Set[str], Dict[Tuple[str, str], str], str, Set[str]]:
    """Aqui cria função de conversção."""

    _, sigma, delta, inicial, final = automata

    novos_estados = set()
    nova_transicao = {}
    estados_nao_processados = [frozenset(epsilon_closure(inicial, delta))]
    mapeando = {frozenset(epsilon_closure(inicial, delta)): 'S0'}
    novo_inicial = 'S0'
    novo_final = set()
    contador = 1

    while estados_nao_processados:
        atual_subset = estados_nao_processados.pop()
        estado_atual_nome = mapeando[atual_subset]

        if not atual_subset.isdisjoint(final):
            novo_final.add(estado_atual_nome)

        novos_estados.add(estado_atual_nome)

        for simbolo in sigma:
            proximo_subset = frozenset(
                dest for estado in atual_subset
                if (estado, simbolo) in delta
                for dest in (
                    delta[(estado, simbolo)]
                    if isinstance(delta[(estado, simbolo)], list)
                    else [delta[(estado, simbolo)]]
                )
                for dest in epsilon_closure(dest, delta)
            )

            if proximo_subset:
                if proximo_subset not in mapeando:
                    mapeando[proximo_subset] = f'S{proximo_subset}'
                    estados_nao_processados.append(proximo_subset)
                    contador += 1

                nova_transicao[(estado_atual_nome, simbolo)] = mapeando[proximo_subset]

    return novos_estados, sigma, nova_transicao, novo_inicial, novo_final
