from __future__ import absolute_import
from celery import shared_task
from sentiment.classifier import NBClassifier
from django.conf import settings
import os.path
from website.models import Comment


@shared_task
def run_classifier(docs):
    path = os.path.join(settings.BASE_DIR, 'sentiment', 'NaiveBayes')
    nb = NBClassifier.load(path)
    result = nb.predict(docs)
    for doc in result:
        try:
            comment = Comment.objects.get(id=doc['id'])
            comment.polarity = doc['polarity']
            comment.save()
        except Comment.DoesNotExist:
            continue