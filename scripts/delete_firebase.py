from google.cloud import firestore
import yaml
fb_key_path = "/mnt/data1/PycharmProjects/research/duongdhk_research/paper_recommender_web/configs/paper-recommender-system-firebase-adminsdk-h3zcq-4add4f9c7b.json"

with open(fb_key_path) as f:
    secret_key = yaml.load(f, Loader=yaml.SafeLoader)
firebase_db = firestore.Client.from_service_account_info(secret_key)

doc_ref = firebase_db.collection("tracking_data")
all_documents = doc_ref.get()
for doc in all_documents:
    doc.reference.delete()

