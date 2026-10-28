# Proyecto de Automatización de Redes - Sucursal 01
**Institución:** Corporación Universitaria Reformada  
**Asignatura:** Gestión de Infraestructura de Redes  

## Descripción del Proyecto
Este proyecto implementa un esquema de automatización e Infraestructura como Código (IaC) para la configuración, respaldo y auditoría de la topología de red de la Sucursal 01.

## Estructura del Repositorio
- `inventario/hosts.yml`: Define los dispositivos gestionados (`SW-SUC-01-CORE` y `SW-SUC-01-ACC1`) y los parámetros de conexión SSH.
- `variables/sucursal_01.yml`: Contiene la declaración centralizada de VLANs (`USUARIOS_VLAN10`, `USUARIOS_VLAN20`, `GESTION`) y la asignación de puertos de acceso y troncales.
- `playbooks/configurar_switches.yml`: Playbook de Ansible que aplica la configuración L2/L3, asegura la idempotencia y genera copias de seguridad de la *running-config*.
- `respaldos/`: Carpeta local donde se almacenan las configuraciones obtenidas de los equipos Cisco.
- `auditoria.py`: Script en Python encargado de verificar el cumplimiento normativo de las VLANs y troncales en los archivos de respaldo.

## Roles de Ansible y Python
- **Ansible:** Actúa como el orquestador principal de Infraestructura como Código. Se encarga del aprovisionamiento uniforme de las VLANs, la asignación de puertos y el guardado de la configuración en NVRAM, garantizando idempotencia en las ejecuciones.
- **Python:** Cumple el rol de motor de auditoría y cumplimiento normativo. Examina los respaldos generados por Ansible para certificar de forma independiente que los dispositivos cumplan al 100% con los estándares exigidos.

## Instrucciones de Ejecución
1. Ejecutar el playbook de Ansible:
   ```bash
   ansible-playbook -i inventario/hosts.yml playbooks/configurar_switches.yml
