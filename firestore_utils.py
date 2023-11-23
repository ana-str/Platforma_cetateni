import base64

from google.cloud import storage, firestore

import os
import shutil


def get_object(db, doc_id):
    doc_ref = db.collection("users").document(doc_id)

    # Get the document
    doc = doc_ref.get()

    if doc.exists:
        # Convert Firestore document data to a Python dictionary
        data = doc.to_dict()
        return data

    return None


def save_image(object):
    storage_client = storage.Client()
    bucket = storage_client.bucket("hacathon-405514.appspot.com")
    image_blob_name = 'static/' + object['cnp'] + '_face.png'

    # Get the blob (file) from the bucket
    blob = bucket.blob(image_blob_name)

    local_image_filename = 'static/face.jpg'
    blob.download_to_filename(local_image_filename)


def save_base64_image(base64_image_data, file_name='saved_image.jpg'):
    # Extract the content after 'base64,' to remove the metadata prefix
    base64_data = base64_image_data.split(',')[1]

    # Decode Base64 to bytes
    image_data = base64.b64decode(base64_data)

    # Save the image to a file
    with open(file_name, 'wb') as file:
        file.write(image_data)


def download_file_from_local_folder(file_name="cerere_eliberare_act_identitate_.pdf", source_folder="static",
                                    destination_folder="/home/cosmin/Downloads"):
    if os.path.exists(source_folder) and os.path.exists(destination_folder):
        file_path = os.path.join(source_folder, file_name)
        dest_path = os.path.join(destination_folder, file_name)

        if os.path.isfile(file_path):
            try:
                shutil.copy2(file_path, dest_path)
            except Exception as e:
                pass  # Handle the exception silently if needed
