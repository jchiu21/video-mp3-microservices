import pika, json 

def upload(f, fs, channel, access):
    try:
        # put the file in the gridFS
        fid = fs.put(f) # returns the file id if successful
    except Exception as err:
        return "internal server error", 500
    
    message = {
        "video_fid": str(fid),
        "mp3_fid": None,
        "username": access["username"] # get username from token claim
    }
    
    # put message on rabbitMQ
    try:
        channel.basic_publish(
            exchange="", # default exchange automatically binds with queues with routing key equal to queue name
            routing_key="video",
            body=json.dumps(message), # serialize message into json string
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE # ensures message is persisted to disk
            )
        )
    except:
        fs.delete(fid) # delete file from gridFS cannot be published to rabbitMQ
        return "internal server error", 500
        
        