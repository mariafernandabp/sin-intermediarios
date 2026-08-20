UNIDADES = ["", "UN", "DOS", "TRES", "CUATRO", "CINCO", "SEIS", "SIETE", "OCHO", "NUEVE"]
DIEZ_A_DIECINUEVE = ["DIEZ", "ONCE", "DOCE", "TRECE", "CATORCE", "QUINCE", "DIECISEIS",
                     "DIECISIETE", "DIECIOCHO", "DIECINUEVE"]
DECENAS = ["", "", "VEINTE", "TREINTA", "CUARENTA", "CINCUENTA", "SESENTA", "SETENTA",
           "OCHENTA", "NOVENTA"]
CENTENAS = ["", "CIENTO", "DOSCIENTOS", "TRESCIENTOS", "CUATROCIENTOS", "QUINIENTOS",
            "SEISCIENTOS", "SETECIENTOS", "OCHOCIENTOS", "NOVECIENTOS"]


def _tres_cifras(n):
    if n == 0:
        return ""
    if n == 100:
        return "CIEN"
    c, resto = divmod(n, 100)
    partes = []
    if c:
        partes.append(CENTENAS[c])
    if resto:
        if resto < 10:
            partes.append(UNIDADES[resto])
        elif resto < 20:
            partes.append(DIEZ_A_DIECINUEVE[resto - 10])
        else:
            d, u = divmod(resto, 10)
            if u == 0:
                partes.append(DECENAS[d])
            elif d == 2:
                partes.append("VEINTI" + UNIDADES[u].lower().upper())
            else:
                partes.append(DECENAS[d] + " Y " + UNIDADES[u])
    return " ".join(partes)


def numero_a_letras(n):
    """Convierte un entero no negativo (pesos colombianos) a texto en mayusculas."""
    n = int(n)
    if n == 0:
        return "CERO PESOS M/CTE"

    millones, resto_m = divmod(n, 1_000_000)
    miles, unidades = divmod(resto_m, 1_000)

    partes = []
    if millones:
        if millones == 1:
            partes.append("UN MILLON")
        else:
            partes.append(_tres_cifras(millones) + " MILLONES")
    if miles:
        if miles == 1:
            partes.append("MIL")
        else:
            partes.append(_tres_cifras(miles) + " MIL")
    if unidades:
        partes.append(_tres_cifras(unidades))

    texto = " ".join(p for p in partes if p).strip()
    sufijo = "PESO M/CTE" if n == 1 else "PESOS M/CTE"
    return f"{texto} {sufijo}"
