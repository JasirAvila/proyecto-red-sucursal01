#!/usr/bin/env python3
"""
validar_inventario.py - Conciliacion entre IPAM (JSON) y variables de diseno (YAML).
Clasifica en: Coincidencias, Faltantes y Diferencias.
"""
import json
from pathlib import Path
import yaml
BASE = Path(__file__).resolve().parent.parent
IPAM_FILE = BASE / "datos" / "ipam_sucursal_01.json"
YAML_FILE = BASE / "variables" / "sucursal_01.yml"
def main():
    print("=" * 76)
    print(" PROTOTIPO 4: CONCILIACION DE FUENTES (IPAM JSON vs YAML DE RED)")
    print("=" * 76)
    with open(IPAM_FILE, "r", encoding="utf-8") as f:
        ipam = json.load(f)
    with open(YAML_FILE, "r", encoding="utf-8") as f:
        diseno = yaml.safe_load(f)
    coincidencias = []
    faltantes = []
    diferencias = []
    vlans_yaml = {v["vlan_id"]: v["name"] for v in diseno.get("vlans", [])}
    # Evaluar Subredes y VLANs
    for item in ipam.get("subredes", []):
        vid = item["vlan_id"]
        if vid in vlans_yaml:
            if item["nombre"] == vlans_yaml[vid]:
                coincidencias.append(f"VLAN {vid} ({item['nombre']}): Definida identica en IPAM y diseno YAML.")
            else:
                diferencias.append(f"VLAN {vid}: Nombre en IPAM '{item['nombre']}' difiere de YAML '{vlans_yaml[vid]}'.")
        else:
            faltantes.append(f"VLAN {vid} ({item['nombre']}): Registrada en IPAM pero AUSENTE en el YAML de red.")
    # Evaluar Dispositivos e Inventario
    dispositivos_yaml = diseno.get("dispositivos", {})
    for disp in ipam.get("dispositivos", []):
        dname = disp["nombre"]
        if dname in dispositivos_yaml:
            coincidencias.append(f"Equipo {dname} [{disp['rol']}]: Coincide en IPAM y en el inventario.")
        else:
            faltantes.append(f"Equipo {dname}: Registrado en IPAM pero ausente en inventario Ansible.")
    print("\n[+] COINCIDENCIAS DETECTADAS (Fuentes alineadas):")
    for c in coincidencias:
        print(f"  [OK] {c}")
    print("\n[-] FALTANTES (Presentes en IPAM pero no desplegadas en la red):")
    for f in faltantes:
        print(f"  [ALERTA] {f}")
    print("\n[!] DIFERENCIAS (Atributos desalineados):")
    if diferencias:
        for d in diferencias:
            print(f"  [ERROR] {d}")
    else:
        print("  [OK] Sin discrepancias de atributos en los elementos comunes.")
    print("\n" + "-" * 76)
    print(f"--> RESUMEN: Coincidencias: {len(coincidencias)} | Faltantes: {len(faltantes)} | Diferencias: {len(diferencias)}")
    print("=" * 76)
if __name__ == "__main__":
    main()
