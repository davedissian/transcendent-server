from flask import copy_current_request_context
from flask_mail import Message
from transcendentserver.extensions import mail
from transcendentserver.constants import MAIL

import Queue
from threading import Thread

class EmptyWorkerPool(Exception):
    pass

mail_queue = Queue.PriorityQueue()
workers = []

def setup_workers():
    def worker():
        while True:
            # Block until a message sender is available to call
            p, msg_sender = mail_queue.get(True) 
            # Then send it
            msg_sender()
            mail_queue.task_done()

    for i in xrange(MAIL.WORKERS):
        t = Thread(target=worker)
        workers.append(t)
        t.daemon = True
        t.start()

def create_message(targets, subject, body, sender):
    subject = subject.encode('utf-8')
    body = body.encode('utf-8')
    return Message(subject, targets, body, sender=sender)

def send(targets, subject, body, sender):
    message = create_message(targets, subject, body, sender) 
    mail.send(message)

def send_async(targets, subject, body, sender, priority=None):
    if not workers:
        raise EmptyWorkerPool
    if priority == None: priority = MAIL.PRIORITY.NORMAL

    @copy_current_request_context
    def send_message():
        send(targets, subject, body, sender)
    mail_queue.put((priority, send_message))
