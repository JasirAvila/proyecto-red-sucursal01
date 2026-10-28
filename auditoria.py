#!/usr/bin/env python3
"""
auditoria.py - Auditoria de cumplimiento de la Sucursal 01 (modo offline).

Lee el diseno esperado desde variables/sucursal_01.yml y la evidencia
obtenida por Ansible desde la carpeta respaldos/. No abre sesiones SSH
ni configura dispositivos.
"""
import re
import sys
from pathlib import Path

import yaml

BASE = Path(__file__).resolve().parent
DISENO = BASE / "variables" / "sucursal_01.yml"
RESPALDOS = BASE / "respaldos"


def leer(ruta):
    return ruta.read_text(encoding="utf-8", errors="ignore") if ruta.exists() else None


def interfaces_de(running):
    """Devuelve {nombre_interfaz: [lineas del bloque]}."""
    bloques, actual = {}, None
    for linea in running.splitlines():
        if linea.startswith("interface "):
            actual = linea.split(None, 1)[1].strip()
            bloques[actual] = []
        elif actual and linea.startswith(" "):
            bloques[actual].append(linea.strip())
        else:
            actual = None
    return bloques


def valor(lineas, prefijo):
    for linea in lineas:
        if linea.lower().startswith(prefijo.lower()):
            return linea[len(prefijo):].strip()
    return None


def expandir(texto):
    conjunto = set()
    for parte in texto.split(","):
        parte = parte.strip()
        if "-" in parte:
            a, b = parte.split("-")
            conjunto.update(range(int(a), int(b) + 1))
        elif parte:
            conjunto.add(int(parte))
    return conjunto


def vlans_permitidas(lineas):
    permitidas = None
    for linea in lineas:
        m = re.match(r"switchport trunk allowed vlan (add )?(.+)$", linea)
        if not m:
            continue
        if not re.fullmatch(r"[\d,\-]+", m.group(2)):
            return {m.group(2)}
        nuevas = expandir(m.group(2))
        permitidas = (permitidas or set()) | nuevas if m.group(1) else nuevas
    return permitidas


def tabla_vlans(vlan_brief):
    vlans = {}
    for linea in vlan_brief.splitlines():
        m = re.match(r"^(\d+)\s+(\S+)\s+(active|act/unsup|suspended|act/lshut|sus/lshut)\b", linea)
        if m:
            vlans[int(m.group(1))] = {"name": m.group(2), "status": m.group(3)}
    return vlans


def comparar(difs, condicion, esperado, encontrado):
    if encontrado is None:
        encontrado = "no configurado"
    if str(esperado) != str(encontrado):
        difs.append(f"{condicion}: esperado '{esperado}', encontrado '{encontrado}'")


class Resultado:
    def __init__(self, dispositivo):
        self.dispositivo = dispositivo
        self.total = 0
        self.cumplen = 0
        print("\n" + "=" * 60)
        print(f" AUDITORIA DE CUMPLIMIENTO: {dispositivo}")
        print("=" * 60)

    def verificar(self, elemento, diferencias):
        self.total += 1
        if diferencias:
            print(f" [NO CUMPLE] {elemento}")
            for d in diferencias:
                print(f"      -> {d}")
        else:
            self.cumplen += 1
            print(f" [CUMPLE]    {elemento}")

    @property
    def conforme(self):
        return self.total > 0 and self.cumplen == self.total

    def cerrar(self):
        pct = 100 * self.cumplen / self.total if self.total else 0
        estado = "CONFORME" if self.conforme else "NO CONFORME"
        print(f"--> ESTADO FINAL {self.dispositivo}: {estado} "
              f"({self.cumplen}/{self.total} elementos, {pct:.0f}%)")
        return self.conforme


def revisar_estado(lineas, difs):
    if "shutdown" in lineas:
        difs.append("estado administrativo: esperado 'activa', encontrado 'shutdown'")


def auditar_switch(nombre, diseno, disp):
    r = Resultado(nombre)
    running = leer(RESPALDOS / f"{nombre}_running_config.txt")
    vlan_brief = leer(RESPALDOS / f"{nombre}_vlan_brief.txt")
    if running is None or vlan_brief is None:
        r.verificar("Evidencia de respaldo",
                    [f"faltan archivos de respaldo de {nombre} en respaldos/"])
        return r.cerrar()

    tabla = tabla_vlans(vlan_brief)
    for v in diseno["vlans"]:
        difs = []
        real = tabla.get(v["vlan_id"])
        if real is None:
            difs.append("la VLAN no existe en el switch")
        else:
            comparar(difs, "nombre", v["name"], real["name"])
            comparar(difs, "estado", "active", real["status"])
        r.verificar(f"VLAN {v['vlan_id']} ({v['name']})", difs)

    interfaces = interfaces_de(running)

    for p in disp["acceso"]:
        difs = []
        lineas = interfaces.get(p["interface"])
        if lineas is None:
            difs.append("la interfaz no aparece en el running-config")
        else:
            comparar(difs, "modo", "access", valor(lineas, "switchport mode "))
            comparar(difs, "VLAN de acceso", p["vlan"], valor(lineas, "switchport access vlan "))
            comparar(difs, "descripcion", p["description"], valor(lineas, "description "))
            revisar_estado(lineas, difs)
        r.verificar(f"Acceso {p['interface']} (VLAN {p['vlan']})", difs)

    for t in disp["troncales"]:
        difs = []
        lineas = interfaces.get(t["interface"])
        if lineas is None:
            difs.append("la interfaz no aparece en el running-config")
        else:
            comparar(difs, "modo", "trunk", valor(lineas, "switchport mode "))
            comparar(difs, "VLAN nativa", t["native_vlan"],
                     valor(lineas, "switchport trunk native vlan "))
            esperadas = expandir(str(t["allowed_vlans"]))
            reales = vlans_permitidas(lineas)
            if reales != esperadas:
                mostrar = "no configurado" if reales is None else ",".join(map(str, sorted(reales, key=str)))
                difs.append(f"VLAN permitidas: esperado '{','.join(map(str, sorted(esperadas)))}', "
                            f"encontrado '{mostrar}'")
            comparar(difs, "descripcion", t["description"], valor(lineas, "description "))
            revisar_estado(lineas, difs)
        r.verificar(f"Troncal {t['interface']}", difs)

    return r.cerrar()


def auditar_router(nombre, disp):
    r = Resultado(nombre)
    running = leer(RESPALDOS / f"{nombre}_running_config.txt")
    if running is None:
        r.verificar("Evidencia de respaldo", [f"falta el respaldo de {nombre} en respaldos/"])
        return r.cerrar()

    interfaces = interfaces_de(running)

    fisica = disp["interfaz_fisica"]
    difs = []
    lineas = interfaces.get(fisica["interface"])
    if lineas is None:
        difs.append("la interfaz no aparece en el running-config")
    else:
        comparar(difs, "descripcion", fisica["description"], valor(lineas, "description "))
        revisar_estado(lineas, difs)
    r.verificar(f"Interfaz fisica {fisica['interface']}", difs)

    for s in disp["subinterfaces"]:
        difs = []
        lineas = interfaces.get(s["interface"])
        if lineas is None:
            difs.append("la subinterfaz no existe")
        else:
            enc = f"{s['vlan']}" + (" native" if s.get("native") else "")
            comparar(difs, "encapsulacion dot1Q", enc, valor(lineas, "encapsulation dot1Q "))
            comparar(difs, "direccion IP", f"{s['ip']} {s['mask']}", valor(lineas, "ip address "))
            comparar(difs, "descripcion", s["description"], valor(lineas, "description "))
            revisar_estado(lineas, difs)
        r.verificar(f"Subinterfaz {s['interface']} (VLAN {s['vlan']})", difs)

    return r.cerrar()


def main():
    diseno = yaml.safe_load(DISENO.read_text(encoding="utf-8"))
    resultados = []
    for nombre, disp in diseno["dispositivos"].items():
        if disp["tipo"] == "router":
            resultados.append(auditar_router(nombre, disp))
        else:
            resultados.append(auditar_switch(nombre, diseno, disp))
        print()

    if all(resultados):
        print(">>> AUDITORIA GENERAL: LA RED CUMPLE EL DISENO DEFINIDO <<<")
        sys.exit(0)
    print(">>> AUDITORIA GENERAL: SE ENCONTRARON DESVIACIONES <<<")
    sys.exit(1)


if __name__ == "__main__":
    main()
