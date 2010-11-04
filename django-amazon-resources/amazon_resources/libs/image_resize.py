import Image

def image_resize(source_file, target_filename, new_width, new_height=None):
    img = Image.open(source_file)
    w, h = img.size
    if img.size[0] < new_width:
        if not new_height or img.size[1] < new_height:
            img.save(target_filename or source_file)
    else:
        wpercent = (new_width / float(img.size[0]))
        if new_height:
            hpercent = (new_height / float(img.size[1]))
        else:
            hpercent = 0
        if wpercent < hpercent or not new_height:
            hsize = int((float(img.size[1]) * float(wpercent)))
            img = img.resize((new_width, hsize), Image.ANTIALIAS)
            w = new_width
            h = hsize
        else:
            wsize = int((float(img.size[0]) * float(hpercent)))
            img = img.resize((wsize, new_height), Image.ANTIALIAS)
            w = wsize
            h = new_height
        img.save(target_filename or source_file)
    return w, h
