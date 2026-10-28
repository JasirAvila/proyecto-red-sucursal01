# Proyecto de Automatización de Redes - Sucursal 01

**Institución:** Corporación Universitaria Reformada
**Asignatura:** Gestión de la Infraestructura de Red
**Estudiante:** Jasir Andrés Ávila Ávila
**Docente:** Miller José Baldovino

## Descripción
Automatización y auditoría de la Sucursal 01 con Ansible y Python sobre una
topología Cisco IOS en GNS3. Ansible aplica y respalda la configuración;
Python audita la evidencia y determina si la red cumple el diseño definido.

## Dispositivos administrados
| Equipo | Gestión | Rol |
|---|---|---|
| R-SUC-01 | 192.168.99.1 | Router, enrutamiento inter-VLAN con subinterfaces |
| SW-SUC-01-CORE | 192.168.99.2 | Switch core |
| SW-SUC-01-ACC1 | 192.168.99.3 | Switch de acceso |

Switch1 (capa 2, conecta PC8) no se incluye en el inventario ni se configura.

## Redes
| VLAN | Nombre | Red | Gateway |
|---|---|---|---|
| 10 | USUARIOS_VLAN10 | 192.168.10.0/24 | 192.168.10.1 |
| 20 | USUARIOS_VLAN20 | 192.168.20.0/24 | 192.168.20.1 |
| 99 | GESTION | 192.168.99.0/24 | 192.168.99.1 |

## Estructura del repositorio
- `inventario/hosts.yml`: dispositivos y credenciales de conexión.
- `variables/sucursal_01.yml`: diseño esperado (VLAN, puertos, troncales, descripciones, subinterfaces).
- `playbooks/configurar_switches.yml`: aplica la configuración y genera los respaldos.
- `respaldos/`: running-config de los tres equipos y `show vlan brief` de los switches.
- `auditoria.py`: auditoría de cumplimiento en Python.
- `ansible.cfg`: configuración de Ansible.

## Rol de Ansible
Ansible configura y respalda. Lee el diseño desde `variables/sucursal_01.yml`,
crea las VLAN, configura troncales 802.1Q (VLAN nativa 99, permitidas 10,20,99),
puertos de acceso y descripciones, configura las subinterfaces del router,
guarda en NVRAM y almacena los respaldos en el servidor. Es idempotente:
una segunda ejecución no realiza cambios (`changed=0`) si el diseño ya se cumple.

## Rol de Python
Python solo audita. `auditoria.py` lee el diseño esperado desde el YAML y la
evidencia obtenida por Ansible desde `respaldos/`. No abre sesiones SSH ni
configura equipos. Verifica existencia, nombre y estado de las VLAN; modo,
VLAN y descripción de los puertos de acceso; modo, VLAN nativa, VLAN permitidas
y descripción de los troncales; y las subinterfaces del router. Para cada
elemento muestra CUMPLE o NO CUMPLE y, si hay diferencia, la condición que no
coincide (valor esperado y encontrado).

## Ejecución
```bash
# 1. Aplicar configuración y generar respaldos
ansible-playbook -i inventario/hosts.yml playbooks/configurar_switches.yml

# 2. Segunda ejecución (debe mostrar changed=0)
ansible-playbook -i inventario/hosts.yml playbooks/configurar_switches.yml

# 3. Solo actualizar respaldos
ansible-playbook -i inventario/hosts.yml playbooks/configurar_switches.yml --tags respaldo

# 4. Auditar (requiere python3-yaml)
python3 auditoria.py
```
