import os
import time
import bluriness_metric
import shutil

tmp_previous_name = ""
tmp_previous_blur = 0
file_name_done = None


def deamon():
    global file_name_done
    global tmp_previous_blur
    global tmp_previous_name

    path = os.path.dirname(os.path.abspath(__file__))
    print("path : ", path)

    file_name = os.listdir(path + "/img_proc/images")
    tmp_previous_name = file_name[0]

    while True:
        time.sleep(10)
        for name in file_name:
            if " " not in name and ".fig" not in name and ".png" in name:
                # img_png = Image.open(path + "/img_proc/images/" + name)
                # img_png.save(
                #    path + "/img_proc/images/" + name[:-4] + ".jpeg", compress=0
                # )
                print(path + "/img_proc/images/" + name[:-5] + ".jpeg")
                tmp = bluriness_metric.blurre_lapace_var(
                    path + "/img_proc/images/" + name[:-5] + ".jpeg"
                )
                print(tmp)
                if tmp_previous_blur == 0 or (
                    tmp < tmp_previous_blur + 100 and tmp > tmp_previous_blur - 100
                ):
                    print("ok")
                    tmp_previous_name = name[:-5] + ".jpeg"
                    tmp_previous_blur = tmp
                else:
                    print("delete")
                    os.remove(path + "/img_proc/images/" + name[:-5] + ".jpeg")
                    print("copy of : ", tmp_previous_name)
                    shutil.copy(
                        path + "/img_proc/images/" + tmp_previous_name,
                        path + "/img_proc/images/" + name[:-5] + ".jpeg",
                    )
                    # file_name = os.listdir(path + "/img_proc/images")

        file_name = [
            files
            for files in os.listdir(path + "/img_proc/images")
            if files not in file_name
        ]
