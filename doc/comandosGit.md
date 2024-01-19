# Comandos para el flujo básico

* Me tira el estado actual del repositorio local respecto del index
>git status

* Realiza dos tareas: trackea archivos nuevos o actualiza cambios a archivos existes
>git add <nombre/s archivo/s> 

* Comenta los cambios realizados en el archivo. Está la forma corta o larga:
>git commit -m "Mensaje corto sobre los cambios"

>git commit <nombre/s archivo/s>

* Actualiza el respositorio local con lo que está en el remoto
>git pull 

* Sube los cambios del repositorio local al remoto
>git push 


# Comandos para el uso de ramas (*branch*)

* Hacer una nueva rama
>git branch nombreRama

* Para ir a esa nueva rama
>git checkout nombreRama

* Se hace el flujo de trabajo de siempre. Pero al commitear, todo se hace en la rama nueva

* Para hacer el merge, se debe ir primero a la rama principal
>git checkout nombreRama

>git merge nombreRama

* Para eliminar la rama
>git branch -d nombreRama


* Para ver las ramas actuales, se ejecuta
>git log
o
>git branch



* En caso de conflicto, porque se modificó la misma línea, por ejemplo, se debe abrir el archivo
y elegir manualmente lo que se desea. Luego se realiza el add, el commit y se pushea.
