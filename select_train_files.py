import os
from shutil import copyfile as copy

base_path = '/data/Mengying/stereo-magnification/RealEstate10K_p/'


def get_video_info(filepath):
    with open(filepath) as f:
        video_url = f.readline().rstrip()
        time_stamps = []
        for l in f.readlines():
            line = l.split(' ')
            time_stamp = int(line[0])
            time_stamps.append(time_stamp)

    youtube_id_offset = video_url.find("/watch?v=") + len('/watch?v=')
    youtube_id = video_url[youtube_id_offset:]

    return youtube_id, time_stamps


train_path = os.path.join("{}/train".format(base_path))

part_path = "{}/train_part".format(base_path)
if not os.path.exists(part_path):
    os.mkdir(part_path)

for file in os.listdir(train_path):
    file_path = os.path.join(train_path, file)
    video_id, time_stamps = get_video_info(file_path)

    image_path = "{}/images/{}".format(base_path, video_id)
    if os.path.exists(image_path):
        i = 0
        for time_stamp in time_stamps:
            if not os.path.exists("{}/{}_{}.jpg".format(image_path, video_id, time_stamp)):
                break
            i += 1
        if i == len(time_stamps):
            copy(file_path, "{}/train_part/{}".format(base_path, file))
