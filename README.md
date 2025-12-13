# Sistema de Órdenes de Reparación (Repair Orders) | Prueba Dacodes

Este proyecto implementa un sistema de gestión de Repair Orders usando:

- Arquitectura hexagonal (Dominio / Aplicación / Infraestructura / Drivers)
- FastAPI (como driver HTTP)
- Repositorios InMemory (para órdenes y eventos)
- Pytest para pruebas

---

## 1. Configuración inicial

### 1.1. Crear y activar un entorno virtual

Desde la raíz del proyecto:

```bash
# Crear entorno virtual
python -m venv .venv

# Activar en Linux / macOS
source .venv/bin/activate
```

### 1.2. Instalar dependencias.

```bash
pip install -r requirements.txt
```

## 2. Ejecutar la API

Para levantar el servidor FastAPI:

```bash
python main.py run
```
Por defecto la aplicación se expone en http://127.0.0.1:8000.

### Ejemplo de payload JSON (*/process-orders/* Metodo POST)
Ejemplo de payload válido que recorre el flujo completo y termina en DELIVERED:

```json
{
  "commands": [
    {
      "op": "CREATE_ORDER",
      "ts": "2025-03-01T10:00:00Z",
      "data": {
        "order_id": "R001",
        "customer": "ACME",
        "vehicle": "ABC-123"
      }
    },
    {
      "op": "ADD_SERVICE",
      "ts": "2025-03-01T10:05:00Z",
      "data": {
        "order_id": "R001",
        "service": {
          "description": "Engine repair",
          "labor_estimated_cost": "10000.00",
          "components": [
            {
              "description": "Oil pump",
              "estimated_cost": "1500.00"
            }
          ]
        }
      }
    },
    {
      "op": "SET_STATE_DIAGNOSED",
      "ts": "2025-03-01T10:10:00Z",
      "data": {
        "order_id": "R001"
      }
    },
    {
      "op": "AUTHORIZE",
      "ts": "2025-03-01T10:11:00Z",
      "data": {
        "order_id": "R001"
      }
    },
    {
      "op": "SET_STATE_IN_PROGRESS",
      "ts": "2025-03-01T10:15:00Z",
      "data": {
        "order_id": "R001"
      }
    },
    {
      "op": "SET_REAL_COST",
      "ts": "2025-03-01T10:20:00Z",
      "data": {
        "order_id": "R001",
        "service_index": 1,
        "real_cost": "14674.00",
        "completed": true
      }
    },
    {
      "op": "TRY_COMPLETE",
      "ts": "2025-03-01T10:25:00Z",
      "data": {
        "order_id": "R001"
      }
    },
    {
      "op": "DELIVER",
      "ts": "2025-03-01T10:30:00Z",
      "data": {
        "order_id": "R001"
      }
    }
  ]
}
```

## 3. Ejecutar los tests

Desde la raíz del proyecto (con el entorno virtual activado):

```bash
pytest
```


## 4. Estructura general del proyecto

```text
app/
  domain/
    entities.py        # Entidades de dominio (RepairOrder, Service, Component, etc.)
    errors.py          # Códigos de error de dominio (ErrorCode)
    ports.py           # Puertos de dominio (OrderRepositoryPort, EventRepositoryPort)
    helpers/
      rounding.py      # Helper round_amount (ROUND_HALF_EVEN)
  application/
    dtos.py            # CommandDTO, ResultDTO, etc.
    orders_service.py  # Servicio que ejecuta comandos y construye el ResultDTO
    use_cases/         # Command handlers (AuthorizeHandler, AddServiceHandler, etc.)
  infrastructure/
    in_memory_repos.py # Implementaciones InMemory de los repos de órdenes y eventos
  drivers/
    http_api.py        # Router FastAPI: driver HTTP que expone el endpoint JSON

main.py                # FastAPI app factory y entrada para `python main.py run`
tests/
  ...                  # Suite de pytest cubriendo los casos de prueba principales

```