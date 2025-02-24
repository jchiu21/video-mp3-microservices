import pika, sys, os, time
from pymongo import MongoClient, mongo_client
import gridfs
from convert import to_mp3

def main():
    client = MongoClient("host.minikube.internal", 27017) # connect to mongoDB server running at host.minikube.internal

    # creates gridFS instances for video and mp3 databases
    fs_videos = gridfs.GridFS(client.videos)
    fs_mp3s = gridfs.GridFS(client.mp3s)
    
    # rabbitmq connection
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq")) # service name resolves to host ip
    channel = connection.channel()
    
    def callback(ch, method, properties, body):
        err = to_mp3.start(body, fs_videos, fs_mp3s, ch)
        if err: 
            ch.basic_nack(delivery_tag=method.delivery_tag) # negative acknowledgement
        else:
            ch.basic_ack(delivery_tag=method.delivery_tag)
    
    # consume message from queue
    channel.basic_consume(
        queue=os.environ.get("VIDEO_QUEUE"),
        on_message_callback=callback   
    )
    
    print("Waiting for messages. To exit press CTRL+C")
    
    channel.start_consuming()
    
if __name__ == "__main__":
    try:
        main()
    
    # handle program termination gracefully
    except KeyboardInterrupt:
        print("Interrupted ")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)