# Prototipos de Python Aplicados a Redes - Sucursal 01 y 02
**Institución:** Corporación Universitaria Reformada  
**Facultad:** Ingeniería - Programa de Ingeniería Informática  
**Asignatura:** Gestión de la Infraestructura de Red  
**Estudiante:** Jasir Andrés Ávila Ávila  
**Docente:** Miller José Baldovino  
## Propósito General
Desarrollo y validación de cinco prototipos en Python orientados a operaciones habituales de ingeniería de redes sobre una infraestructura Cisco IOS automatizada con Ansible en GNS3.
## Resumen de Prototipos Implementados
1. **Validación Antes y Después (`python/validar_cambio.py`):** Pre/post check de cambios no disruptivos garantizando la integridad de elementos críticos (VLAN 99, enlaces troncales y gestión).
2. **Generación de Datos de Diseño (`python/generar_sucursal_02.py`):** Algoritmo VLSM sobre el bloque `10.20.0.0/23` que genera variables estructuradas en `variables/sucursal_02_generada.yml`.
3. **Auditoría de Flota (`python/auditar_flota.py`):** Auditoría multicriterio de sistema operativo e interfaces operativas para R-SUC-01, CORE y ACC1, exportando a `evidencias/auditoria_flota.csv`.
4. **Relación de Fuentes de Información (`python/validar_inventario.py`):** Conciliación automática entre fuente de verdad IPAM (JSON) y diseño de red (YAML), identificando coincidencias y faltantes.
5. **Medición de Conectividad de Gestión (`python/medir_conectividad.py`):** Evaluación de SLA mediante 10 pruebas ICMP por equipo y registro en `evidencias/mediciones_conectividad.csv`.
