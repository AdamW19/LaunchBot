# From Splatbot: https://github.com/ktraw2/SplatBot/blob/master/modules/gif_generator.py

import datetime
from modules.async_client import AsyncClient
from modules.splatoon_rotation import SplatoonRotation
from modules.execute import render_gif


async def generate_gif(rotation_info: SplatoonRotation, channel_id: str, bot):
    # Making sure we have the images to put together
    if rotation_info is None or rotation_info.stage_images is None:
        raise AttributeError("Files to generate gif does not exist")

    # setting up the image name and image/gif file names
    image_base = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "-" + str(channel_id)

    image_filenames = []
    for i in range(len(rotation_info.stage_images)):
        filename = image_base + "-{}.png".format(str(i))
        image_filenames.append(filename)

    gif_filename = image_base + ".gif"

    # getting the images and saving them locally
    client = AsyncClient(session=bot.session)
    for i in range(len(rotation_info.stage_images)):
        await client.send_image_request(image_url=rotation_info.stage_images[i], file_path=image_filenames[i])

    # making the gif
    await render_gif(image_base, gif_filename)

    # returning the name of the gif on file
    return gif_filename
