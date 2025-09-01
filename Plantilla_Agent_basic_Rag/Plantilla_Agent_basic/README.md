#Estandarizando el desarrollo de agentes IA para CUNAUTI :

Esta plantilla tiene como base:

(estructura de archivos + integración de modelo + prompt_template)


    #Plantilla Desarrollado en base a la primera version de Hector repliker.

    Se busca :
        agilizar el proceso de desarrollo de los agentes IA en general (Replikers , repli , etc)


-----------------------------------------------------------
#para poder activar el entorno virtual en shell :

python -m venv venv
venv\Scripts\Activate
pip install -r requirements.txt



#para comprobar la conexion con el mongo DB atlas
python config.py

#para ejecutar main.py ----->agente (modelo+prompt_template)
python -m  agent.main 
-------------------------------------------------------------