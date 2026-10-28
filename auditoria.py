import os
import sys

def auditar_respaldo(dispositivo, vlan_requeridas, puertos_troncales):
    archivo_path = f"respaldos/{dispositivo}_running_config.txt"
    if not os.path.exists(archivo_path):
        print(f"[FALLO] No se encontro el archivo de respaldo para {dispositivo}")
        return False

    with open(archivo_path, 'r') as f:
        contenido = f.read()

    print(f"\n==========================================")
    print(f" AUDITORIA DE CUMPLIMIENTO: {dispositivo}")
    print(f"==========================================")

    contenido_lower = contenido.lower()
    vlans_ok = True

    for vlan_id, vlan_nombre in vlan_requeridas.items():
        vlan_str = f"vlan {vlan_id}"
        vlan_access_str = f"access vlan {vlan_id}"
        vlan_native_str = f"native vlan {vlan_id}"
        vlan_allowed_str = f"allowed vlan"

        if (vlan_str in contenido_lower or 
            vlan_access_str in contenido_lower or 
            vlan_native_str in contenido_lower or 
            (vlan_allowed_str in contenido_lower and vlan_id in contenido_lower) or
            vlan_nombre.lower() in contenido_lower):
            print(f" [+] VLAN {vlan_id} ({vlan_nombre}): OK")
        else:
            print(f" [-] VLAN {vlan_id} ({vlan_nombre}): NO ENCONTRADA O INCORRECTA")
            vlans_ok = False


    troncales_ok = True
    for intf in puertos_troncales:
        if f"interface {intf}".lower() in contenido_lower and "switchport mode trunk" in contenido_lower:
            print(f" [+] Troncal Interface {intf}: OK")
        else:
            print(f" [-] Troncal Interface {intf}: NO CONFIGURADA EN TRUNK")
            troncales_ok = False

    cumple = vlans_ok and troncales_ok
    estado = "CONFORME (100%)" if cumple else "NO CONFORME"
    print(f"--> ESTADO FINAL {dispositivo}: {estado}\n")
    return cumple

def main():
    vlans_obligatorias = {
        "10": "USUARIOS_VLAN10",
        "20": "USUARIOS_VLAN20",
        "99": "GESTION"
    }

    core_troncales = ["GigabitEthernet0/0", "GigabitEthernet1/2"]
    acc1_troncales = ["GigabitEthernet0/0"]

    res_core = auditar_respaldo("SW-SUC-01-CORE", vlans_obligatorias, core_troncales)
    res_acc1 = auditar_respaldo("SW-SUC-01-ACC1", vlans_obligatorias, acc1_troncales)

    if res_core and res_acc1:
        print(">>> AUDITORIA GENERAL COMPLETADA CON EXITO <<<")
        sys.exit(0)
    else:
        print(">>> AUDITORIA ENCONTRÓ DESVIACIONES DE CONFIGURACIÓN <<<")
        sys.exit(1)

if __name__ == "__main__":
    main()
