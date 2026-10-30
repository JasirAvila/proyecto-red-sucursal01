#!/usr/bin/env python3
"""
medir_conectividad.py - Ejecuta 10 pings ICMP hacia cada equipo de gestion,
calcula metricas de latencia, evalua SLA y exporta a archivo CSV.
"""
import csv
from datetime import datetime
from pathlib import Path
import re
import subprocess
BASE = Path(__file__).resolve().parent.parent
CSV_SALIDA = BASE / "evidencias" / "mediciones_conectividad.csv"
DESTINOS = [
    {"equipo": "R-SUC-01", "ip": "192.168.99.1"},
    {"equipo": "SW-SUC-01-CORE", "ip": "192.168.99.2"},
    {"equipo": "SW-SUC-01-ACC1", "ip": "192.168.99.3"}
]
def hacer_ping(ip):
    cmd = ["ping", "-c", "10", "-W", "1", ip]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    salida = res.stdout
    m_pkts = re.search(r"(\d+)\s+packets transmitted,\s+(\d+)\s+received,\s+([\d\.]+)%\s+packet loss", salida)
    tx = m_pkts.group(1) if m_pkts else "10"
    rx = m_pkts.group(2) if m_pkts else "0"
    perdida = float(m_pkts.group(3)) if m_pkts else 100.0
    m_rtt = re.search(r"rtt min/avg/max/mdev =\s+([\d\.]+)/([\d\.]+)/([\d\.]+)/", salida)
    if m_rtt:
        lat_min = float(m_rtt.group(1))
        lat_avg = float(m_rtt.group(2))
        lat_max = float(m_rtt.group(3))
    else:
        lat_min, lat_avg, lat_max = 0.0, 0.0, 0.0
    return int(tx), int(rx), perdida, lat_min, lat_avg, lat_max
def main():
    print("=" * 84)
    print(" PROTOTIPO 5: MEDICION DE CONECTIVIDAD Y CALIDAD DE GESTION (10 ICMP)")
    print("=" * 84)
    filas_csv = [["Fecha", "Equipo", "Destino_IP", "Enviados", "Recibidos", "Perdida_Pct", "Lat_Min_ms", "Lat_Avg_ms", "Lat_Max_ms", "SLA_Resultado"]]
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{'Equipo':<16} {'IP Gestion':<16} {'Perdida':<10} {'Latencia Prom':<16} {'SLA Status'}")
    print("-" * 84)
    for item in DESTINOS:
        tx, rx, perdida, l_min, l_avg, l_max = hacer_ping(item["ip"])
        cumple = (perdida == 0.0) and (l_avg <= 50.0)
        sla = "CUMPLE" if cumple else "NO CUMPLE"
        filas_csv.append([fecha, item["equipo"], item["ip"], tx, rx, f"{perdida}%", l_min, l_avg, l_max, sla])
        print(f"{item['equipo']:<16} {item['ip']:<16} {perdida}%{'':<6} {l_avg:.2f} ms{'':<9} [{sla}]")
    # Guardar en archivo CSV
    with open(CSV_SALIDA, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(filas_csv)
    print("-" * 84)
    print(f"[OK] Metricas exportadas exitosamente en:\n     {CSV_SALIDA}\n")
if __name__ == "__main__":
    main()
