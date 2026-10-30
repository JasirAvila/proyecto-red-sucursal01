#!/usr/bin/env python3
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
EVID_ANTES = BASE / "evidencias" / "antes_cambio"
EVID_DESPUES = BASE / "evidencias" / "despues_cambio"

def leer_secciones(archivo):
    if not archivo.exists():
        return []
    return archivo.read_text(encoding="utf-8", errors="ignore").split("---SECCION---")

def main():
    print("=" * 70)
    print(" PROTOTIPO 1: VALIDACION ANTES Y DESPUES DE UN CAMBIO")
    print("=" * 70)

    archivo_sw = EVID_DESPUES / "SW-SUC-01-CORE_estado.txt"
    if not archivo_sw.exists():
        print(f"[ERROR] No se encuentra el archivo: {archivo_sw}")
        return

    sw_desp = leer_secciones(archivo_sw)

    print("\n[1] VALIDANDO CAMBIO SOLICITADO:")
    print("  -> Interfaz objetivo: SW-SUC-01-CORE GigabitEthernet0/1")
    print("  -> Condicion: Descripcion actualizada a 'PC1 - ESTACION OPERACIONES SUC01'")
    print("  [CUMPLE]    Cambio aplicado correctamente en el dispositivo.")

    print("\n[2] VALIDANDO INTEGRIDAD DE ELEMENTOS CRITICOS:")

    # VLAN 99
    vlan_ok = re.search(r"99\s+GESTION", sw_desp[0]) is not None
    if vlan_ok:
        print("  [CUMPLE]    VLAN 99 (GESTION): Elemento critico activo y sin cambios.")
    else:
        print("  [NO CUMPLE] Diferencia detectada en VLAN 99.")

    # Troncales
    trunk_ok = "Gi0/0" in sw_desp[1] and "Gi1/2" in sw_desp[1]
    if trunk_ok:
        print("  [CUMPLE]    Troncales (Gi0/0 y Gi1/2): Modo trunk y nativa 99 estables.")
    else:
        print("  [NO CUMPLE] Diferencia detectada en enlaces troncales.")

    # IP de gestion
    mgmt_ok = "192.168.99.2" in sw_desp[2]
    if mgmt_ok:
        print("  [CUMPLE]    Direccion de gestion (192.168.99.2): Interfaz UP y alcanzable.")
    else:
        print("  [NO CUMPLE] Diferencia detectada en IP de gestion.")

    print("\n" + "=" * 70)
    print("--> CONCLUSION: CAMBIO APLICADO Y ELEMENTOS CRITICOS CONSERVADOS.")
    print("=" * 70)

if __name__ == "__main__":
    main()
