import boto3
import json
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
import uuid

expediente = "752929"
nombre_completo = "Fabricio Daniel Lara Valencia"

app = FastAPI(title="Practica 4")

s3_client = boto3.client('s3')
sqs_client = boto3.client('sqs')

BUCKET_NAME = f"practica-4-{expediente}"
QUEUE_NAME = "cola-boletines"

@app.post("/boletines")
async def crear_boletin(file: UploadFile = File(...), mensaje: str = Form(...), correo: str = Form(...)):
    try:
        boletin_id = str(uuid.uuid4())
        file_name = file.filename
        s3_client.upload_fileobj(file.file, BUCKET_NAME, file_name)
        link_s3 = f"https://{BUCKET_NAME}.s3.us-east-1.amazonaws.com/{file_name}"
        contenido_mensaje = {
            "id": boletin_id,
            "mensaje": mensaje,
            "correo": correo,
            "url_imagen": link_s3
        }

        queue_url = sqs_client.get_queue_url(QueueName=QUEUE_NAME)['QueueUrl']
        sqs_client.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(contenido_mensaje)
        )

        return {
            "status": "procesado",
            "s3_url": link_s3,
            "sqs_status": "mensaje enviado"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

preguntas = """
1. ¿Qué función cumple SQS dentro de esta arquitectura?
Actua como un mensajero enter el emisor y el receptor este recibe las solicitudes de generacion de boletines y las almacena hasta que el receptor pueda procesarlas\n\n
2. ¿Por qué es útil desacoplar el emisor del receptor?
Creo que la mayor ventaja que tiene es el que si uno de los dos falla el otro puede mantenerse funcionando, tambien supongo que se puede hacer un escalamiento horizontal, donde si tienes muchos correos por procesar peude creer mas contenedores de este servicio para que mas rapidamente se vaya liberando \n\n
3. ¿Qué ventajas ofrece SNS en este flujo?
Pues creo que al ser un servicio de amazon que esta desacoplado de mi codigo puedo cambiar el metodo de distribucion del mensaje sin cambair nada del codigo \n\n
4.¿Qué ventajas y desventajas ves al utilizar colas para gestionar la comunicación entre contenedores en contraste a protocolos sincrónicos como HTTP?  
al hacerlo con colas el emisor no espera el receptor este puede seguir haciendo su trabajo de inmedaito y en caso que el receptor falle de alguna manera la informacion no se pierde sino que queda en la cola y se consume despues y las desventajas de las colas es que un modelo sincronico no requiere una estructura adicional como en este caso la cola lo cual puede ser mas complejo ademas que no necesita manejar logica contar duplicados \n\n
5.¿Cuál consideras que sería una manera de incrementar la resiliencia de la aplicación en caso de que el envío de un mensaje falle?
Pues puede ser el manejar una cola distinta donde se guarden los mensajes que no pudieron ser procesados y borrarlo de la cola principal asi pudiendo diferenciar los mensajes con mayor prioridad en falla y atendiendolos mas rapido \n\n
6.¿Qué otro método crees que exista para el monitoreo de mensajes de manera sincrónica además de colas/notificaciones?
No se si los sockets cuenten como un metodo de cmonicacion bidireccional entre cliente-servidor \n\n
"""

conclusiones = """
Conclusion \n
Esta practica fue bastante buena de aprender porque entendi como e usa la dockerizacion y como puedo usar los recursos de la nube para llevarlo a cabo, tambien nunca habia utilizado una cola como mensajero entre dos servicios lo que resulto interesante, como puntos importantes creo que aprendi el uso de sqs como una cola estandar para poder comunicar dos servicios y como evitar los deuplciados para evitar usar una cola FIFO tambien como dividir el proyecto en varios contenedores que funcionen como servicios separados para que funcionen entre si y el uso del docker-compose para orquestar estos contenedores
"""

if __name__ == "__main__":
    print("Evaluación de la práctica 4")
    print(f"Nombre del alumno: {nombre_completo}")
    print(f"Expediente: {expediente}")
    print(preguntas)
    print(conclusiones)
