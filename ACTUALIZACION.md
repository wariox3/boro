# Script de actualización — boro

`/root/actualizar_boro.sh` actualiza boro en producción: baja los cambios de `main`, reinstala dependencias, reinicia el servicio y muestra si responde en el puerto 8055.

Requiere la instalación descrita en [DESPLIEGUE.md](DESPLIEGUE.md): código en `/opt/boro`, usuario `boro`, entorno virtual en `/opt/boro/.venv` y servicio systemd `boro`.

## Script

```bash
#!/bin/bash
set -e

cd /opt/boro
sudo -u boro git checkout -- __pycache__ 2>/dev/null || true
sudo -u boro git pull origin main
sudo -u boro .venv/bin/pip install -r requirements.txt
systemctl restart boro
sleep 3
systemctl status boro --no-pager
curl -s http://127.0.0.1:8055/
echo
```

| Línea | Qué hace |
| --- | --- |
| `set -e` | Detiene el script en el primer comando que falle |
| `git checkout -- __pycache__` | Descarta el `.pyc` versionado en commits antiguos, que bloquearía el `git pull` |
| `git pull origin main` | Baja los últimos cambios de GitHub |
| `pip install -r requirements.txt` | Instala dependencias nuevas o actualizadas |
| `systemctl restart boro` | Reinicia el servicio con el código nuevo |
| `systemctl status` y `curl` | Muestra el estado del servicio y la respuesta de `GET /` |

## Instalación

Como root en el servidor:

```bash
nano /root/actualizar_boro.sh      # pegar el script
chmod 700 /root/actualizar_boro.sh
```

## Uso

```bash
sudo /root/actualizar_boro.sh
```

Termina bien si el estado muestra `active (running)` y la última línea es `{"Hello":"World"}`.

## Si falla

| Síntoma | Solución |
| --- | --- |
| `git pull` falla por cambios locales | `cd /opt/boro && sudo -u boro git status`, descartar con `sudo -u boro git checkout -- <archivo>` y repetir |
| `git pull` pide usuario y contraseña | El repo es privado: configurar una deploy key para el usuario `boro` |
| El estado no es `active (running)` o no aparece `{"Hello":"World"}` | `journalctl -u boro -n 50` para ver el error |
| La versión nueva no funciona | Volver atrás: `cd /opt/boro && sudo -u boro git checkout <commit_anterior> && systemctl restart boro` |

El script no hace rollback automático. Se probó en una simulación local (repo de prueba y `systemctl`/`curl` simulados); aún no se ha ejecutado en el servidor real.
