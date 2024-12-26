def dv_patentes():
    number_by_letter = {
        "A": "14", "B": "01", "C": "00", "D": "16", "E": "05", "F": "20",
        "G": "19", "H": "09", "I": "24", "J": "07", "K": "21", "L": "08",
        "M": "04", "N": "13", "O": "25", "P": "22", "Q": "18", "R": "10",
        "S": "02", "T": "06", "U": "12", "V": "23", "W": "11", "X": "03",
        "Y": "15", "Z": "17"
    }

    def get_dv(patente):
        # Convertir a mayúsculas y remover espacios o guiones
        patente = patente.upper().replace(" ", "").replace("-", "")

        # Reemplazar letras por números
        numbers = patente
        for letter, number in number_by_letter.items():
            numbers = numbers.replace(letter, number)

        # Inicializar sumas
        num1 = 0
        num2 = 0

        # Sumar valores de índices pares e impares
        for i, char in enumerate(numbers):
            if i % 2 == 0:
                num1 += int(char)
            else:
                num2 += int(char)

        # Reducir números a una cifra
        num1 = reduce_number(num1)
        num2 = reduce_number(num2)

        return str(num1) + str(num2)

    def reduce_number(n):
        # Reducir a una sola cifra
        while isinstance(n, int) and len(str(n)) > 1:
            n = sum(int(digit) for digit in str(n))
        return n

    return {"get_dv": get_dv}
