#!/usr/bin/env python3
"""
generar_sucursal_02.py - Calcula subredes VLSM y genera el YAML de variables.
"""
import ipaddress
import math
from pathlib import Path
import yaml
BASE = Path(__file__).resolve().parent.parent
ENTRADA = BASE / "datos" / "sucursal_02_entrada.yml"
SALIDA = BASE / "variables" / "sucursal_02_generada.yml"
def calcular_prefijo(hosts):
    total_necesario = hosts + 3  # hosts + gateway + red + broadcast
    bits_host = math.ceil(math.log2(total_necesario))
    return 32 - bits_host
def main():
    print("=" * 78)
    print(" PROTOTIPO 2: PLANIFICACION VLSM Y GENERACION DE VARIABLES (SUCURSAL 02)")
    print("=" * 78)
    with open(ENTRADA, "r", encoding="utf-8") as f:
        datos = yaml.safe_load(f)
    superred = ipaddress.ip_network(datos["bloque_disponible"])
    requerimientos = sorted(datos["redes_requeridas"], key=lambda x: x["hosts_requeridos"], reverse=True)
    resultado_vlans = []
    ip_cursor = int(superred.network_address)
    print(f"\nBloque asignado: {superred}")
    print(f"{'VLAN':<6} {'Nombre':<16} {'Red Calculada':<18} {'Mascara':<16} {'Gateway':<14} {'Capacidad'}")
    print("-" * 78)
    for item in requerimientos:
        prefijo = calcular_prefijo(item["hosts_requeridos"])
        subred = ipaddress.ip_network(f"{ipaddress.IPv4Address(ip_cursor)}/{prefijo}")
        gateway = list(subred.hosts())[0]
        capacidad = subred.num_addresses - 2
        resultado_vlans.append({
            "vlan_id": item["vlan_id"],
            "name": item["nombre"],
            "network": str(subred.network_address),
            "prefix": prefijo,
            "netmask": str(subred.netmask),
            "gateway": str(gateway),
            "hosts_previstos": item["hosts_requeridos"],
            "hosts_disponibles": capacidad
        })
        print(f"{item['vlan_id']:<6} {item['nombre']:<16} {str(subred.network_address) + '/' + str(prefijo):<18} "
              f"{str(subred.netmask):<16} {str(gateway):<14} {capacidad} hosts")
        ip_cursor += subred.num_addresses
    # Guardar archivo YAML estructurado para Ansible
    yaml_salida = {
        "sucursal": "SUC-02",
        "red_base": datos["bloque_disponible"],
        "vlans": resultado_vlans
    }
    with open(SALIDA, "w", encoding="utf-8") as f:
        yaml.dump(yaml_salida, f, default_flow_style=False, sort_keys=False)
    print("-" * 78)
    print(f"[OK] Archivo YAML generado con exito en:\n     {SALIDA}\n")
if __name__ == "__main__":
    main()
