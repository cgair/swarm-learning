import os

CLUSTER = ["localhost:12345", "localhost:23456"]
MODEL_DIR = "./checkpoints/"

def file_prepared(epoch, batch):
    model_name = 'weights.{:0>2}-{:0>2}.hdf5'.format(epoch, batch)
    model_path = MODEL_DIR + model_name
    print(f"model path = {model_path}")
    if os.path.exists(model_path):
        return True, model_path
    return False, ""
